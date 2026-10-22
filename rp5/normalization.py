from __future__ import annotations

import re
from typing import Any, Optional

from rp5.domain import FindingCard, Lesion

# Plausible range for lesion measurements in breast imaging (mm)
MIN_PLAUSIBLE_SIZE_MM = 0.1
MAX_PLAUSIBLE_SIZE_MM = 300.0

# Supported mammographic views
VALID_VIEWS = {"CC", "MLO", "ML", "LM", "XCCL", "AT", "TAN", "SPOT", "MAG"}

# Valid BI-RADS breast density categories
VALID_DENSITY_CATEGORIES = {"A", "B", "C", "D"}

# Valid laterality options
VALID_LATERALITY = {"left", "right", "bilateral"}

# Regex for explicit measurement units
_MEASUREMENT_RE = re.compile(
    r"(?i)\b(\d+(?:\.\d+)?)\s*(mm|millimeter|millimeters|cm|centimeter|centimeters)\b"
)


def extract_measurement(text: str) -> tuple[Optional[float], list[str]]:
    """
    Extract a lesion measurement from free text using conservative parsing.
    Returns (normalized_size_mm, warnings).
    Compatible units such as centimeters are converted to millimeters.
    """
    if not text:
        return None, []

    warnings: list[str] = []
    matches = _MEASUREMENT_RE.findall(text)
    if not matches:
        return None, []

    # If multiple distinct measurements found, warn about ambiguity
    parsed_values: list[float] = []
    for val_str, unit in matches:
        try:
            val = float(val_str)
        except ValueError:
            continue
        unit_lower = unit.lower()
        if unit_lower.startswith("cm") or unit_lower.startswith("centimeter"):
            val_mm = val * 10.0
        else:
            val_mm = val

        if val_mm < MIN_PLAUSIBLE_SIZE_MM or val_mm > MAX_PLAUSIBLE_SIZE_MM:
            warnings.append(
                f"Measurement {val_str} {unit} ({val_mm:.1f} mm) is outside plausible clinical range "
                f"[{MIN_PLAUSIBLE_SIZE_MM}, {MAX_PLAUSIBLE_SIZE_MM}] mm and was rejected."
            )
            continue

        parsed_values.append(val_mm)

    if not parsed_values:
        return None, warnings

    if len(parsed_values) > 1 and len(set(round(v, 1) for v in parsed_values)) > 1:
        warnings.append(
            f"Multiple distinct measurements found in text '{text}': "
            f"{[f'{v:.1f} mm' for v in parsed_values]}. Using primary measurement {parsed_values[0]:.1f} mm."
        )

    return parsed_values[0], warnings


def clean_location_text(location: str) -> tuple[str, Optional[float], list[str]]:
    """
    Extract measurement embedded in location text, and return cleaned location.
    E.g. 'upper outer quadrant, 12.0 mm' -> ('upper outer quadrant', 12.0, []).
    """
    if not location:
        return "", None, []

    warnings: list[str] = []
    size_mm, meas_warnings = extract_measurement(location)
    warnings.extend(meas_warnings)

    cleaned = _MEASUREMENT_RE.sub("", location)
    # Clean up trailing/leading commas, parentheses, or whitespace
    cleaned = re.sub(r"[,;()]+", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    return cleaned or location.strip(), size_mm, warnings


def normalize_lesion(lesion: Lesion | dict[str, Any]) -> tuple[Lesion, list[str]]:
    """
    Normalize a Lesion object or dictionary.
    - Preserves structured measurement if valid.
    - Extracts measurement from location or text if structured is missing.
    - Flags conflicts between structured and textual measurements.
    - Cleans descriptors.
    """
    warnings: list[str] = []
    if isinstance(lesion, dict):
        kind = str(lesion.get("kind", "mass")).strip()
        location = str(lesion.get("location", "")).strip()
        size_mm = lesion.get("size_mm")
        descriptors = list(lesion.get("descriptors", []) or [])
        hint = lesion.get("assessment_hint")
    else:
        kind = lesion.kind.strip() if lesion.kind else "mass"
        location = lesion.location.strip() if lesion.location else ""
        size_mm = lesion.size_mm
        descriptors = list(lesion.descriptors or [])
        hint = lesion.assessment_hint

    cleaned_location, text_size, loc_warnings = clean_location_text(location)
    warnings.extend(loc_warnings)

    final_size_mm: Optional[float] = None

    if size_mm is not None:
        try:
            structured_val = float(size_mm)
            if structured_val < MIN_PLAUSIBLE_SIZE_MM or structured_val > MAX_PLAUSIBLE_SIZE_MM:
                warnings.append(
                    f"Structured size_mm ({structured_val}) is outside plausible range "
                    f"[{MIN_PLAUSIBLE_SIZE_MM}, {MAX_PLAUSIBLE_SIZE_MM}] mm and was rejected."
                )
            else:
                final_size_mm = structured_val
        except (ValueError, TypeError):
            warnings.append(f"Invalid non-numeric structured size_mm: {size_mm}")

    if final_size_mm is not None and text_size is not None:
        if abs(final_size_mm - text_size) > 0.5:
            warnings.append(
                f"Discrepancy detected: structured size ({final_size_mm:.1f} mm) conflicts "
                f"with textual measurement ({text_size:.1f} mm). Preserving structured value."
            )
        location = cleaned_location
    elif final_size_mm is None and text_size is not None:
        final_size_mm = text_size
        location = cleaned_location

    norm_descriptors = [str(d).strip() for d in descriptors if d and str(d).strip()]

    return Lesion(
        kind=kind,
        location=location,
        size_mm=final_size_mm,
        descriptors=norm_descriptors,
        assessment_hint=hint,
    ), warnings


def normalize_finding_card(card: FindingCard | dict[str, Any]) -> tuple[FindingCard, list[str]]:
    """
    Normalize FindingCard fields:
    - Normalizes each lesion and its measurements.
    - Validates modality, laterality, breast density.
    - Does NOT convert '0.5' into a valid density category or 'not available' into a view.
    """
    warnings: list[str] = []
    if isinstance(card, dict):
        case_id = str(card.get("case_id", "UNKNOWN"))
        modality = str(card.get("modality", "MG")).strip().upper()
        laterality = str(card.get("laterality", "")).strip().lower()
        breast_density = card.get("breast_density")
        raw_lesions = card.get("lesions", [])
        birads = card.get("birads")
        pathology = card.get("pathology")
        reason = str(card.get("reason_for_exam", "")).strip()
    else:
        case_id = card.case_id
        modality = card.modality.strip().upper() if card.modality else "MG"
        laterality = card.laterality.strip().lower() if card.laterality else ""
        breast_density = card.breast_density
        raw_lesions = card.lesions
        birads = card.birads
        pathology = card.pathology
        reason = card.reason_for_exam.strip() if card.reason_for_exam else ""

    # Validate breast density
    norm_density: Optional[str] = None
    if breast_density is not None:
        density_str = str(breast_density).strip().upper()
        if density_str in VALID_DENSITY_CATEGORIES:
            norm_density = density_str
        else:
            warnings.append(
                f"Invalid breast density '{breast_density}'; expected BI-RADS category (A, B, C, or D). Set to null."
            )
            norm_density = None

    # Validate laterality
    if laterality and laterality not in VALID_LATERALITY:
        warnings.append(
            f"Unrecognized laterality '{laterality}'; expected one of {VALID_LATERALITY}."
        )

    norm_lesions: list[Lesion] = []
    for lesion_item in raw_lesions:
        n_lesion, l_warn = normalize_lesion(lesion_item)
        norm_lesions.append(n_lesion)
        warnings.extend(l_warn)

    norm_card = FindingCard(
        case_id=case_id,
        modality=modality,
        laterality=laterality,
        breast_density=norm_density,
        lesions=norm_lesions,
        birads=birads,
        pathology=pathology.strip() if pathology else None,
        reason_for_exam=reason,
    )
    return norm_card, warnings


def normalize_view(view: Any) -> tuple[Optional[str], list[str]]:
    """
    Normalize radiographic view.
    Does not convert 'not available' into a valid view.
    """
    if view is None:
        return None, []
    v_str = str(view).strip().upper()
    if v_str in VALID_VIEWS:
        return v_str, []
    if v_str in ("NOT AVAILABLE", "N/A", "UNKNOWN", "NONE", ""):
        return None, ["Imaging view not specified in source."]
    return None, [f"Unrecognized imaging view '{view}'; expected standard projection (e.g. CC, MLO)."]
