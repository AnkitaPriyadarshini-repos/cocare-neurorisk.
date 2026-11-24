"""Dynamic Form Specification Generator.

Derives ml/artifacts/form_spec.json and backend/models/form_spec.json directly from
the active dataset variable mapping configuration (e.g. oasis_mapping.yaml or lasi_dad_mapping.yaml).
Enables zero-friction transition between cohorts without breaking frontend schema contracts.
"""
import os
import json
import argparse
import yaml
from typing import Dict, Any


def generate_form_spec_from_mapping(mapping_path: str, output_paths: list = None) -> Dict[str, Any]:
    """Generate form_spec.json from YAML variable mapping."""
    with open(mapping_path, "r", encoding="utf-8") as f:
        mapping = yaml.safe_load(f)
        
    dataset_name = mapping.get("dataset_name", "OASIS-demo")
    schema_version = mapping.get("schema_version", "1.1.0")
    
    fields = []
    for var in mapping.get("variables", []):
        field_def = {
            "name": var["standard_name"],
            "label": var.get("label", var["standard_name"]),
            "label_or": var.get("label_or", f"{var['standard_name']} [needs native review]"),
            "type": var.get("type", "number"),
            "required": var.get("required", True),
            "help_text": var.get("help_text", ""),
            "help_text_or": var.get("help_text_or", "[needs native review]"),
            "model_variant": var.get("model_variant", "both")
        }
        
        if field_def["type"] == "number":
            field_def["min"] = var.get("min", 0)
            field_def["max"] = var.get("max", 100)
            field_def["step"] = var.get("step", 1)
            
        elif field_def["type"] == "select":
            options = []
            for opt in var.get("options", []):
                opt_str = str(opt)
                if opt_str == "M":
                    opt_label = "Male"
                    opt_or = "ପୁରୁଷ [needs native review]"
                elif opt_str == "F":
                    opt_label = "Female"
                    opt_or = "ମହିଳା [needs native review]"
                else:
                    opt_label = opt_str
                    opt_or = f"{opt_str} [needs native review]"
                options.append({
                    "value": opt,
                    "label": opt_label,
                    "label_or": opt_or
                })
            field_def["options"] = options
            
        fields.append(field_def)
        
    form_spec = {
        "schema_version": schema_version,
        "dataset": dataset_name,
        "model_status": "demo_oasis_not_validated_for_lasi_dad",
        "disclaimer": "This tool is a cognitive risk screening aid designed for preliminary assessment, NOT a clinical diagnosis. Results must be interpreted by qualified healthcare professionals.",
        "disclaimer_or": "ଏହି ଉପକରଣଟି କେବଳ ଏକ ପ୍ରାଥମିକ ଜ୍ଞାନଗତ ବିପଦ ଯାଞ୍ଚ ସହାୟକ, କୌଣସି ଡାକ୍ତରୀ ନିଦାନ ନୁହେଁ। [needs native review]",
        "fields": fields
    }
    
    if output_paths:
        for out_path in output_paths:
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(form_spec, f, indent=2, ensure_ascii=False)
                
    return form_spec


def main():
    parser = argparse.ArgumentParser(description="Generate form_spec.json from mapping YAML.")
    parser.add_argument("--mapping", type=str, default="ml/config/oasis_mapping.yaml", help="Path to mapping YAML.")
    args = parser.parse_args()
    
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    mapping_path = os.path.join(base_dir, args.mapping) if not os.path.isabs(args.mapping) else args.mapping
    
    output_paths = [
        os.path.join(base_dir, "ml", "artifacts", "form_spec.json"),
        os.path.join(base_dir, "backend", "models", "form_spec.json")
    ]
    
    spec = generate_form_spec_from_mapping(mapping_path, output_paths)
    print(f"SUCCESS: Generated form_spec.json from '{mapping_path}' for dataset '{spec['dataset']}' (schema_version {spec['schema_version']}).")


if __name__ == "__main__":
    main()
