# -*- coding: utf-8 -*-
"""
backend/ml/class_mappings.py
Single source of truth for all crop-to-disease-class mappings.
Extracted from app.py / interface.py to avoid duplication.
"""

CLASS_MAPPINGS: dict[str, list[str]] = {
    "Tomato":   ["bacterial_spot", "early_blight", "Fusarium Wilt", "healthy_leaf",
                 "late_blight", "leaf_curl", "leaf_miner", "leaf_mold",
                 "septoria_leaf", "spider mites", "verticillium wilt"],
    "Apple":    ["Apple black_spot", "Apple Brown_spot", "Apple Normal"],
    "Apricot":  ["Apricot blight leaf disease", "Apricot Normal", "Apricot shot_hole"],
    "Beans":    ["Bean bean rust image", "Bean Fungal_leaf disease",
                 "Bean Normal leaf", "Bean shot_hole"],
    "Brinjal":  ["Healthy Leaf", "Insect Pest Disease", "Leaf Spot Disease",
                 "Mosaic Virus Disease", "White Mold Disease", "Wilt Disease"],
    "Cashew":   ["Cashew healthy", "Cashew leaf miner", "Cashew red rust"],
    "cherry":   ["Cherry brown_spot", "Cherry Leaf Scorch", "Cherry Normal leaf",
                 "Cherry purple leaf spot", "Cherry_shot hole disease"],
    "Corn":     ["Corn Fungal leaf", "Corn gray leaf spot",
                 "Corn holcus_ leaf spot", "Corn Normal leaf"],
    "Cucumber": ["Anthracnose", "Bacterial Wilt", "Belly Rot", "Downy Mildew",
                 "Fresh Cucumber", "Fresh Leaf", "Gummy Stem Blight", "Pythium Fruit Rot"],
    "Fig":      ["Fig Blight_leaf disease", "Fig Brown spot",
                 "Fig normal leaf", "Fig_rust leaf"],
    "Grape":    ["Grape Anthracnose leaf", "Grape Brown spot leaf",
                 "Grape Downy mildew leaf", "Grape Mites_leaf disease",
                 "Grape Normal_leaf", "Grape Powdery_mildew leaf",
                 "Grape shot hole leaf disease"],
    "Guava":    ["Canker", "Curling", "Healthy", "Leaf Spot",
                 "Nutritional Deficiency", "Powdery Mildew", "Rust"],
    "Lychee":   ["Algal Spot Indirect", "Anthracnose Cloudy", "Dry Leaves",
                 "Entomosporium Spot", "Leaf Mites Direct", "Mayetiola PostRain"],
    "Potato":   ["Fungi", "Healthy", "Nematode"],
    "Radish":   ["Black leaf spot", "Downey mildew", "flea beetle",
                 "Fresh leaf", "Mosaic virus"],
    "Rice":     ["bacterial_leaf_blight", "brown_spot", "leaf_blast", "rice_healthy"],
    "Walnut":   ["Walnut Anthracnose_leaf disease", "Walnut Blotch_leaf disease",
                 "Walnut leaf gall mite", "Walnut Normal_leaf", "Walnut Shot_hole"],
}

# Crops with lower accuracy that should always show an uncertainty warning
LOW_ACCURACY_CROPS: set[str] = {"Brinjal"}  # 65.43%

# Confidence threshold below which an uncertainty warning is shown
CONFIDENCE_THRESHOLD: float = 0.60

# Human-readable crop names for UI display
CROP_DISPLAY_NAMES: dict[str, str] = {
    "Tomato":   "Tomato",
    "Apple":    "Apple",
    "Apricot":  "Apricot",
    "Beans":    "Beans",
    "Brinjal":  "Brinjal (Eggplant)",
    "Cashew":   "Cashew",
    "cherry":   "Cherry",
    "Corn":     "Corn (Maize)",
    "Cucumber": "Cucumber",
    "Fig":      "Fig",
    "Grape":    "Grape",
    "Guava":    "Guava",
    "Lychee":   "Lychee",
    "Potato":   "Potato",
    "Radish":   "Radish",
    "Rice":     "Rice",
    "Walnut":   "Walnut",
}
