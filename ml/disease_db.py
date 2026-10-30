# -*- coding: utf-8 -*-
"""
backend/ml/disease_db.py
Centralised agricultural disease database — extended to all 17 supported crops.
Reusable by both the Gradio app and the FastAPI backend.

IMPORTANT: These are general guidance notes for awareness purposes only.
Farmers should consult their local Krishi Vigyan Kendra (KVK) or
a licensed agronomist before applying any treatment.
"""

from typing import TypedDict

KVK_DEFAULT_REMEDY = (
    "Contact your nearest Krishi Vigyan Kendra (KVK) for a crop-specific "
    "recommendation tailored to your local conditions."
)


class DiseaseEntry(TypedDict):
    cause: str
    remedy: str
    impact: str
    severity: str          # "healthy" | "medium" | "high"
    symptoms: list[str]
    preventive_measures: list[str]


AGRI_DATABASE: dict[str, dict[str, DiseaseEntry]] = {
    # ─────────────────────────────── TOMATO ───────────────────────────────
    "tomato": {
        "late_blight": {
            "cause": "Phytophthora infestans (water mould)",
            "remedy": (
                "Apply Chlorothalonil or Mancozeb at 7-day intervals. "
                "Use Trichoderma harzianum for organic control. "
                "Remove and destroy infected foliage."
            ),
            "impact": "Can destroy 75–100% of crop within 10 days under wet conditions.",
            "severity": "high",
            "symptoms": [
                "Dark water-soaked lesions on leaves and stems",
                "White mouldy growth on undersides of leaves",
                "Rapid leaf collapse and blackening",
                "Brown rot on green and ripe fruit",
            ],
            "preventive_measures": [
                "Use certified disease-free seed",
                "Avoid overhead irrigation",
                "Apply protective fungicide before rainy season",
                "Maintain plant spacing for good airflow",
            ],
        },
        "early_blight": {
            "cause": "Alternaria solani fungus",
            "remedy": (
                "Apply Azoxystrobin or Copper-based fungicide. "
                "Ensure proper plant spacing for airflow."
            ),
            "impact": "Reduces yield by 20–30%; defoliates plants progressively.",
            "severity": "medium",
            "symptoms": [
                "Brown target-like concentric ring spots on older leaves",
                "Yellow halo surrounding dark lesions",
                "Progressive lower-leaf defoliation",
                "Stem lesions at soil line (collar rot)",
            ],
            "preventive_measures": [
                "Crop rotation with non-solanaceous crops",
                "Remove infected plant debris",
                "Apply mulch to prevent soil splash",
                "Ensure balanced nitrogen fertilisation",
            ],
        },
        "bacterial_spot": {
            "cause": "Xanthomonas vesicatoria bacteria",
            "remedy": (
                "Copper bactericide sprays. "
                "Avoid overhead irrigation. "
                "Crop rotation recommended."
            ),
            "impact": "Significant fruit blemishing; reduces marketable yield by up to 40%.",
            "severity": "medium",
            "symptoms": [
                "Small water-soaked lesions on leaves turning brown",
                "Scabby raised spots on fruits",
                "Defoliation in severe cases",
                "Stem streaking",
            ],
            "preventive_measures": [
                "Use disease-free transplants",
                "Avoid working in wet fields",
                "Apply copper spray at transplanting",
                "Rotate crops for minimum 2 years",
            ],
        },
        "leaf_curl": {
            "cause": "Tomato Yellow Leaf Curl Virus (TYLCV) via whiteflies",
            "remedy": (
                "Apply Imidacloprid to control whitefly vectors. "
                "Use reflective mulch. Remove infected plants early."
            ),
            "impact": "Complete growth stunting; 100% yield loss if untreated.",
            "severity": "high",
            "symptoms": [
                "Upward and inward curling of leaves",
                "Yellowing (chlorosis) of leaf margins",
                "Stunted growth and reduced fruit set",
                "Whitefly colonies visible on undersides",
            ],
            "preventive_measures": [
                "Use TYLCV-resistant varieties",
                "Install yellow sticky traps to monitor whitefly",
                "Apply reflective silver mulch in beds",
                "Eliminate alternate weed hosts",
            ],
        },
        "leaf_miner": {
            "cause": "Liriomyza trifolii (insect larvae)",
            "remedy": (
                "Apply Spinosad or Abamectin. "
                "Introduce natural predators (Diglyphus isaea). "
                "Remove heavily mined leaves."
            ),
            "impact": "Reduces photosynthesis capacity by 30–40%.",
            "severity": "medium",
            "symptoms": [
                "Serpentine white mines/tunnels on leaf surface",
                "Blistered and papery leaf tissue",
                "Tiny black puparia on leaves or soil",
                "Premature leaf drop",
            ],
            "preventive_measures": [
                "Use yellow sticky traps early in season",
                "Avoid broad-spectrum pesticides that kill natural enemies",
                "Plant border crops as trap plants",
                "Remove and bury infested leaf litter",
            ],
        },
        "leaf_mold": {
            "cause": "Passalora fulva fungus (humid conditions)",
            "remedy": (
                "Improve ventilation. "
                "Apply Chlorothalonil or Mancozeb. Reduce leaf wetness."
            ),
            "impact": "Causes defoliation in greenhouse crops; 10–15% yield loss.",
            "severity": "medium",
            "symptoms": [
                "Pale green to yellow spots on upper leaf surface",
                "Olive-green to brown mould on undersides",
                "Affected leaves curl and drop",
                "Severe in warm humid greenhouses",
            ],
            "preventive_measures": [
                "Reduce greenhouse humidity below 85%",
                "Use drip irrigation rather than overhead watering",
                "Space plants for maximum airflow",
                "Prune lower leaves to improve ventilation",
            ],
        },
        "septoria_leaf": {
            "cause": "Septoria lycopersici fungus",
            "remedy": (
                "Remove lower infected leaves. "
                "Apply copper fungicide or Mancozeb every 7–14 days."
            ),
            "impact": "Progressive defoliation; reduces photosynthesis and fruit size.",
            "severity": "medium",
            "symptoms": [
                "Small circular spots with dark border and grey centre",
                "Tiny black dots (pycnidia) within lesions",
                "Affects older leaves first; spreads upward",
                "Rapid defoliation under humid conditions",
            ],
            "preventive_measures": [
                "Remove and destroy infected plant debris",
                "Avoid overhead irrigation",
                "Practice 2-year crop rotation",
                "Apply mulch to reduce soil splash",
            ],
        },
        "spider mites": {
            "cause": "Tetranychus urticae (Two-spotted spider mite)",
            "remedy": (
                "Apply Abamectin or Spiromesifen miticides. "
                "Increase humidity. Introduce Phytoseiulus persimilis predators."
            ),
            "impact": "Causes bronzing and defoliation; severe in hot dry weather.",
            "severity": "medium",
            "symptoms": [
                "Fine yellow stippling on upper leaf surface",
                "Bronze or silver leaf discolouration",
                "Fine webbing on undersides and between leaves",
                "Mite colonies visible with a hand lens",
            ],
            "preventive_measures": [
                "Maintain adequate irrigation to reduce heat stress",
                "Avoid dusty field conditions",
                "Use miticides on rotation to prevent resistance",
                "Conserve natural predator populations",
            ],
        },
        "verticillium wilt": {
            "cause": "Verticillium dahliae soil-borne fungus",
            "remedy": (
                "Soil solarization. "
                "Use resistant varieties (VF-labeled). "
                "Avoid replanting in infected soil."
            ),
            "impact": "Wilting and premature death; entire plant loss likely.",
            "severity": "high",
            "symptoms": [
                "V-shaped yellow lesions on leaf margins",
                "Wilting of lower leaves during hot midday",
                "Brown discolouration of stem vascular tissue",
                "Stunted, low-yielding plants",
            ],
            "preventive_measures": [
                "Solarize soil with clear plastic in summer",
                "Plant certified resistant cultivars",
                "Avoid over-irrigation which favours fungal spread",
                "Rotate with resistant crops (maize, grasses)",
            ],
        },
        "fusarium wilt": {
            "cause": "Fusarium oxysporum f. sp. lycopersici",
            "remedy": (
                "Plant resistant cultivars. "
                "Soil amendment with Trichoderma. Avoid over-irrigation."
            ),
            "impact": "Permanent wilting and plant death; no chemical cure after infection.",
            "severity": "high",
            "symptoms": [
                "Yellowing of lower leaves on one side of plant",
                "Vascular browning visible when stem is cut",
                "Progressive wilting that doesn't recover overnight",
                "Plant death within weeks of infection",
            ],
            "preventive_measures": [
                "Use Fusarium-resistant (F-rated) varieties",
                "Amend soil with Trichoderma viride before planting",
                "Maintain soil pH between 6.5–7.0",
                "Never replant tomato in infected beds for 5 years",
            ],
        },
        "healthy_leaf": {
            "cause": "None",
            "remedy": "Continue regular NPK fertilisation and drip irrigation. Maintain weekly scouting.",
            "impact": "Crop is thriving — optimal conditions detected.",
            "severity": "healthy",
            "symptoms": [],
            "preventive_measures": ["Continue current management practices"],
        },
    },

    # ─────────────────────────────── RICE ────────────────────────────────
    "rice": {
        "bacterial_leaf_blight": {
            "cause": "Xanthomonas oryzae pv. oryzae",
            "remedy": "Apply Copper oxychloride. Use resistant varieties. Drain fields when disease appears.",
            "impact": "Reduces yield by 20–30% in severe cases.",
            "severity": "high",
            "symptoms": [
                "Water-soaked to yellowish stripes on leaf margins",
                "Leaves turn grey-white and wilt",
                "Milky or yellow bacterial ooze from cut ends",
                "Yellowing and drying from leaf tip downwards",
            ],
            "preventive_measures": [
                "Avoid excess nitrogen application",
                "Use disease-resistant varieties (IR64, Swarna-Sub1)",
                "Drain water from fields during outbreak",
                "Apply copper-based bactericides preventively",
            ],
        },
        "brown_spot": {
            "cause": "Helminthosporium oryzae fungus",
            "remedy": "Apply Mancozeb or Propiconazole. Ensure balanced potassium nutrition.",
            "impact": "Reduces grain quality and germination rate.",
            "severity": "medium",
            "symptoms": [
                "Small oval to circular brown spots on leaves",
                "Spots with grey/white centre and brown margin",
                "Grain discolouration and unfilled spikelets",
                "Seedling blight in nurseries",
            ],
            "preventive_measures": [
                "Ensure adequate potassium and silicon nutrition",
                "Use certified, treated seed",
                "Apply organic matter to improve soil health",
                "Proper water management to avoid stress",
            ],
        },
        "leaf_blast": {
            "cause": "Magnaporthe oryzae fungus",
            "remedy": "Apply Tricyclazole or Isoprothiolane at boot stage. Avoid excessive nitrogen.",
            "impact": "Can cause 50–90% yield loss in severe epidemics.",
            "severity": "high",
            "symptoms": [
                "Diamond-shaped lesions with grey centre and brown border",
                "Nodes turn black and break (node blast)",
                "Panicle neck rotting and drooping (neck blast)",
                "Severe in upland rice under cool, humid weather",
            ],
            "preventive_measures": [
                "Use blast-resistant varieties",
                "Avoid late-season nitrogen application",
                "Use silicon fertiliser to strengthen cell walls",
                "Apply systemic fungicide at booting stage",
            ],
        },
        "rice_healthy": {
            "cause": "None",
            "remedy": "Maintain water management and balanced fertilisation. Monitor weekly.",
            "impact": "Excellent crop health — no action required.",
            "severity": "healthy",
            "symptoms": [],
            "preventive_measures": ["Continue current water and nutrient management"],
        },
    },

    # ─────────────────────────────── POTATO ──────────────────────────────
    "potato": {
        "fungi": {
            "cause": "Mixed fungal pathogens (Rhizoctonia solani, Fusarium spp.)",
            "remedy": "Apply Mancozeb or Chlorothalonil foliar spray. Treat seed tubers with Thiram before planting.",
            "impact": "Tuber rot and significant yield reduction.",
            "severity": "high",
            "symptoms": [
                "Black scurf or sclerotia on tuber surface",
                "Brown sunken lesions on stems near soil",
                "Wilting and yellow foliage",
                "Rotting seed pieces in cool wet soil",
            ],
            "preventive_measures": [
                "Use certified disease-free seed tubers",
                "Treat seeds with fungicide before planting",
                "Rotate with cereals or legumes for 3 years",
                "Improve soil drainage to prevent waterlogging",
            ],
        },
        "healthy": {
            "cause": "None",
            "remedy": "Continue hilling and irrigation schedule. Apply balanced NPK.",
            "impact": "Crop is healthy — premium yield expected.",
            "severity": "healthy",
            "symptoms": [],
            "preventive_measures": ["Continue current hilling and irrigation practices"],
        },
        "nematode": {
            "cause": "Root-knot nematodes (Meloidogyne spp.)",
            "remedy": "Soil fumigation with Carbofuran. Crop rotation with non-host crops. Biofumigation with mustard.",
            "impact": "Stunting and 20–70% yield reduction depending on infestation level.",
            "severity": "high",
            "symptoms": [
                "Galls or knots on roots and stolons",
                "Stunted and yellowing plants",
                "Irregular tuber surface with warty growth",
                "Wilting even in adequate soil moisture",
            ],
            "preventive_measures": [
                "Grow marigold (Tagetes spp.) as a trap crop",
                "Use nematode-resistant varieties",
                "Apply neem cake to soil before planting",
                "Maintain 4-year crop rotation with cereals",
            ],
        },
    },

    # ─────────────────────────────── APPLE ───────────────────────────────
    "apple": {
        "apple black_spot": {
            "cause": "Venturia inaequalis (scab fungus)",
            "remedy": "Apply Captan or Myclobutanil at green tip. Prune for canopy airflow. Rake and destroy fallen leaves.",
            "impact": "Fruit becomes unmarketable; up to 70% crop loss.",
            "severity": "high",
            "symptoms": [
                "Olive-green to black velvety spots on leaves",
                "Scab lesions on fruit surface",
                "Fruit cracking and deformation",
                "Premature fruit drop in severe infection",
            ],
            "preventive_measures": [
                "Apply dormant copper spray before bud break",
                "Prune for open canopy to reduce humidity",
                "Rake and compost all fallen leaves",
                "Use scab-resistant apple varieties",
            ],
        },
        "apple brown_spot": {
            "cause": "Marssonina coronaria fungal infection",
            "remedy": "Apply Dithianon or Mancozeb. Improve drainage and reduce humidity.",
            "impact": "Premature defoliation reduces next season yield.",
            "severity": "medium",
            "symptoms": [
                "Small reddish-brown spots on upper leaf surface",
                "Yellow halo around lesions in late season",
                "Early defoliation in July–September",
                "Weakened trees susceptible to other diseases",
            ],
            "preventive_measures": [
                "Remove fallen leaves to break disease cycle",
                "Apply fungicide from petal fall stage",
                "Improve inter-row drainage",
                "Avoid dense planting",
            ],
        },
        "apple normal": {
            "cause": "None",
            "remedy": "Continue seasonal pruning and calcium foliar spray. Maintain pest monitoring.",
            "impact": "Premium fruit yield expected.",
            "severity": "healthy",
            "symptoms": [],
            "preventive_measures": ["Continue dormant pruning and regular monitoring"],
        },
    },

    # ─────────────────────────────── GUAVA ───────────────────────────────
    "guava": {
        "canker": {
            "cause": "Pestalotiopsis psidii fungus",
            "remedy": "Prune infected branches. Apply Copper oxychloride. Avoid mechanical injuries.",
            "impact": "Fruit drop and bark death; reduces yield by 30%.",
            "severity": "high",
            "symptoms": [
                "Raised corky lesions on bark and twigs",
                "Sunken brown cankers girdling branches",
                "Die-back of affected shoots",
                "Premature fruit drop",
            ],
            "preventive_measures": [
                "Avoid wounding bark during cultural operations",
                "Sterilise pruning tools with alcohol",
                "Apply Bordeaux paste to pruning wounds",
                "Remove and burn severely affected branches",
            ],
        },
        "curling": {
            "cause": "Aphid infestation and thrips feeding",
            "remedy": "Spray Imidacloprid or Dimethoate. Use sticky yellow traps.",
            "impact": "New shoot distortion; reduces fruit set.",
            "severity": "medium",
            "symptoms": [
                "Inward or downward curling of young leaves",
                "Distorted and stunted new growth",
                "Honeydew and sooty mould on leaves",
                "Visible aphid colonies on shoot tips",
            ],
            "preventive_measures": [
                "Install yellow sticky traps at canopy level",
                "Conserve natural predators (ladybirds, lacewings)",
                "Apply neem oil spray as preventive",
                "Prune excess vegetative flush during monsoon",
            ],
        },
        "healthy": {
            "cause": "None",
            "remedy": "Apply micronutrient spray. Maintain drip irrigation and mulching.",
            "impact": "Optimal health — full season yield expected.",
            "severity": "healthy",
            "symptoms": [],
            "preventive_measures": ["Continue drip irrigation and mulching practices"],
        },
        "leaf spot": {
            "cause": "Colletotrichum gloeosporioides",
            "remedy": "Apply Carbendazim or Mancozeb. Remove infected leaves before monsoon.",
            "impact": "Defoliation and reduced fruit quality.",
            "severity": "medium",
            "symptoms": [
                "Circular brownish spots with yellow margin",
                "Spots coalesce and cause leaf blight",
                "Premature defoliation in post-monsoon",
                "Mummified fruit with lesions",
            ],
            "preventive_measures": [
                "Remove infected leaves before monsoon onset",
                "Apply copper fungicide prophylactically",
                "Avoid water stress which predisposes trees",
                "Use mulch to prevent soil-borne splash",
            ],
        },
        "nutritional deficiency": {
            "cause": "Zinc or Iron micronutrient deficiency",
            "remedy": "Foliar spray of ZnSO4 (0.5%) or FeSO4 (0.2%). Soil pH correction.",
            "impact": "Reduces fruit size, colour, and taste.",
            "severity": "medium",
            "symptoms": [
                "Interveinal chlorosis (yellowing between veins)",
                "Small, pale, poorly-flavoured fruit",
                "Dieback of young shoots",
                "Reduced flowering and fruit set",
            ],
            "preventive_measures": [
                "Test soil pH annually; maintain 6.0–7.0",
                "Apply chelated micronutrient fertiliser annually",
                "Use balanced NPK with micronutrient supplement",
                "Incorporate organic matter to improve nutrient availability",
            ],
        },
        "powdery mildew": {
            "cause": "Oidium psidii fungus (dry season)",
            "remedy": "Spray Wettable Sulphur or Hexaconazole. Improve air circulation.",
            "impact": "Affects young shoots and fruit skin quality.",
            "severity": "medium",
            "symptoms": [
                "White powdery coating on young leaves and shoots",
                "Distortion and stunting of new growth",
                "Premature fruit drop",
                "Severe in dry weather with cool nights",
            ],
            "preventive_measures": [
                "Prune to open canopy structure",
                "Apply wettable sulphur at first sign",
                "Avoid high nitrogen fertilisation in dry season",
                "Irrigate in morning to allow leaf drying",
            ],
        },
        "rust": {
            "cause": "Puccinia psidii rust fungus",
            "remedy": "Apply Propiconazole or Triadimefon. Avoid excessive nitrogen fertilisation.",
            "impact": "Severe defoliation and reduced photosynthesis.",
            "severity": "high",
            "symptoms": [
                "Bright orange-yellow pustules on undersides",
                "Yellow spots on upper leaf surface",
                "Severe defoliation in wet seasons",
                "Shoot tip dieback",
            ],
            "preventive_measures": [
                "Use rust-tolerant varieties where available",
                "Apply systemic fungicide at first pustule appearance",
                "Avoid dense planting to reduce humidity",
                "Remove infected shoots and leaves",
            ],
        },
    },

    # ─────────────────────────────── APRICOT ─────────────────────────────
    "apricot": {
        "apricot blight leaf disease": {
            "cause": "Pseudomonas syringae pv. syringae bacterial blight",
            "remedy": "Apply copper hydroxide in autumn. Prune infected wood 30cm below lesions.",
            "impact": "Branch dieback can cause 30–50% structural damage to the tree.",
            "severity": "high",
            "symptoms": [
                "Water-soaked lesions on leaves and young shoots",
                "Brown necrotic blotches on leaves",
                "Gummosis (amber resin) on infected branches",
                "Blossom blighting in spring",
            ],
            "preventive_measures": [
                "Apply copper spray at leaf fall and bud burst",
                "Avoid overhead irrigation",
                "Prune during dry weather",
                "Sterilise pruning tools between cuts",
            ],
        },
        "apricot normal": {
            "cause": "None",
            "remedy": "Continue balanced NPK programme. Apply dormant oil in late winter.",
            "impact": "Healthy tree — good fruit yield expected.",
            "severity": "healthy",
            "symptoms": [],
            "preventive_measures": ["Continue dormant spray and balanced fertilisation"],
        },
        "apricot shot_hole": {
            "cause": "Wilsonomyces carpophilus (Coryneum blight / shot-hole fungus)",
            "remedy": "Apply Ziram or Copper fungicide at leaf fall and green tip. Remove infected twigs.",
            "impact": "Reduces photosynthetic area and weakens trees significantly.",
            "severity": "medium",
            "symptoms": [
                "Small reddish-brown circular spots on leaves",
                "Spots drop out leaving shot-hole appearance",
                "Sunken lesions with purple border on twigs",
                "Sticky gum (gummosis) on infected wood",
            ],
            "preventive_measures": [
                "Apply preventive copper spray at bud swell",
                "Remove and burn infected twigs and fallen leaves",
                "Avoid wetting foliage during irrigation",
                "Maintain good orchard sanitation",
            ],
        },
    },

    # ─────────────────────────────── BEANS ───────────────────────────────
    "beans": {
        "bean bean rust image": {
            "cause": "Uromyces appendiculatus rust fungus",
            "remedy": "Apply Triadimefon or Mancozeb at first sign. Remove infected plants.",
            "impact": "Can reduce yield by 30–80% if unchecked.",
            "severity": "high",
            "symptoms": [
                "Orange-red powdery pustules on leaf undersides",
                "Yellow spots on upper leaf surface",
                "Premature defoliation",
                "Severe in warm, humid weather",
            ],
            "preventive_measures": [
                "Plant resistant bean varieties",
                "Space plants for good air circulation",
                "Rotate beans with non-legume crops",
                "Avoid late-afternoon irrigation",
            ],
        },
        "bean fungal_leaf disease": {
            "cause": "Cercospora canescens / Phaeoisariopsis griseola (Angular Leaf Spot)",
            "remedy": "Apply Carbendazim or Copper fungicide. Remove infected debris after harvest.",
            "impact": "Defoliation reduces pod filling; up to 40% yield loss.",
            "severity": "medium",
            "symptoms": [
                "Angular brown lesions bounded by leaf veins",
                "Greyish spore masses on leaf undersides",
                "Lesions on pods causing dark sunken spots",
                "Premature leaf drop",
            ],
            "preventive_measures": [
                "Use disease-free certified seed",
                "Rotate with maize or sorghum",
                "Apply copper spray early in the season",
                "Remove crop debris after harvest",
            ],
        },
        "bean normal leaf": {
            "cause": "None",
            "remedy": "Maintain irrigation schedule and balanced fertilisation.",
            "impact": "Healthy crop — good pod development expected.",
            "severity": "healthy",
            "symptoms": [],
            "preventive_measures": ["Continue regular scouting and balanced NPK application"],
        },
        "bean shot_hole": {
            "cause": "Xanthomonas axonopodis pv. phaseoli (Common Bacterial Blight)",
            "remedy": "Apply Copper bactericide. Use certified seed. Avoid working in wet conditions.",
            "impact": "Pod lesions can lead to 30% marketable yield loss.",
            "severity": "medium",
            "symptoms": [
                "Water-soaked lesions that turn brown with yellow border",
                "Dead tissue drops leaving 'shot-hole' appearance",
                "Greasy water-soaked spots on pods",
                "Vascular discolouration in stems",
            ],
            "preventive_measures": [
                "Plant certified disease-free seed",
                "Treat seed with hot water (50°C for 25 min)",
                "Rotate away from beans for 2+ years",
                "Avoid overhead irrigation",
            ],
        },
    },

    # ─────────────────────────────── BRINJAL ─────────────────────────────
    "brinjal": {
        "healthy leaf": {
            "cause": "None",
            "remedy": "Maintain balanced NPK and regular irrigation. Scout weekly.",
            "impact": "Healthy crop — good fruit yield expected.",
            "severity": "healthy",
            "symptoms": [],
            "preventive_measures": ["Continue regular monitoring and balanced fertilisation"],
        },
        "insect pest disease": {
            "cause": "Leucinodes orbonalis (Brinjal Shoot and Fruit Borer) or Aphis gossypii",
            "remedy": "Apply Spinosad or Emamectin Benzoate. Remove bored shoots immediately. Use pheromone traps.",
            "impact": "Up to 70% fruit damage; heavily reduces marketable yield.",
            "severity": "high",
            "symptoms": [
                "Wilting and drooping of tender shoot tips",
                "Entry holes in fruits with frass",
                "Internal fruit damage with rotting",
                "Larvae visible inside bored shoots",
            ],
            "preventive_measures": [
                "Install pheromone traps at 20/ha",
                "Remove and destroy affected shoots weekly",
                "Use borer-resistant varieties",
                "Apply neem-based spray at flowering",
            ],
        },
        "leaf spot disease": {
            "cause": "Phomopsis vexans (Phomopsis blight) or Cercospora melongenae",
            "remedy": "Apply Mancozeb or Copper oxychloride. Improve field drainage.",
            "impact": "Defoliation and fruit rot; 20–40% yield loss.",
            "severity": "medium",
            "symptoms": [
                "Circular to irregular brown spots with lighter centre",
                "Spots enlarge and coalesce causing blight",
                "Fruit rot with dark sunken lesions",
                "Stem cankers at collar level",
            ],
            "preventive_measures": [
                "Use certified disease-free seed",
                "Rotate with non-solanaceous crops",
                "Maintain proper plant spacing",
                "Apply fungicide at first sign of spots",
            ],
        },
        "mosaic virus disease": {
            "cause": "Brinjal Mosaic Virus (BMV) transmitted by aphids",
            "remedy": "Control aphid vectors with Imidacloprid. Remove infected plants. Use reflective mulch.",
            "impact": "Fruit deformation and 50% reduction in marketable yield.",
            "severity": "high",
            "symptoms": [
                "Mosaic pattern of light and dark green on leaves",
                "Leaf distortion, puckering and curling",
                "Stunted growth and small fruit",
                "Fruit discolouration and deformation",
            ],
            "preventive_measures": [
                "Use virus-resistant varieties",
                "Install yellow sticky traps for aphid monitoring",
                "Rogue out infected plants early",
                "Maintain strict aphid control throughout season",
            ],
        },
        "white mold disease": {
            "cause": "Sclerotinia sclerotiorum white mould fungus",
            "remedy": "Apply Iprodione or Carbendazim. Improve drainage. Increase plant spacing.",
            "impact": "Entire plant collapse; up to 60% stand loss in severe outbreaks.",
            "severity": "high",
            "symptoms": [
                "White cottony mycelial growth on stems",
                "Black sclerotia inside or on stems",
                "Watery rot and stem collapse",
                "Infected plants turn straw-coloured and die",
            ],
            "preventive_measures": [
                "Avoid high plant density",
                "Improve field drainage to prevent waterlogging",
                "Apply systemic fungicide before flowering",
                "Remove and destroy affected plants and debris",
            ],
        },
        "wilt disease": {
            "cause": "Fusarium oxysporum f. sp. melongenae or Verticillium dahliae",
            "remedy": "Soil solarization. Apply Trichoderma viride to soil. Use resistant rootstock.",
            "impact": "Complete plant death; no effective chemical cure post-infection.",
            "severity": "high",
            "symptoms": [
                "Sudden wilting of entire plant during daytime",
                "Brown discolouration of vascular tissue (cut stem)",
                "Leaves turn yellow from base upward",
                "Progressive plant collapse without recovery",
            ],
            "preventive_measures": [
                "Solarize soil before transplanting",
                "Use grafted plants on resistant rootstock",
                "Rotate with non-solanaceous crops for 4+ years",
                "Drench soil with Trichoderma before planting",
            ],
        },
    },

    # ─────────────────────────────── CASHEW ──────────────────────────────
    "cashew": {
        "cashew healthy": {
            "cause": "None",
            "remedy": "Continue balanced NPK and zinc/boron micronutrient sprays.",
            "impact": "Excellent tree health — good nut yield expected.",
            "severity": "healthy",
            "symptoms": [],
            "preventive_measures": ["Continue regular foliar nutrition and pruning"],
        },
        "cashew leaf miner": {
            "cause": "Acrocercops syngramma (Cashew leaf miner moth larvae)",
            "remedy": "Apply Quinalphos or Profenofos. Collect and destroy mined leaves.",
            "impact": "Heavy infestation can cause 20–30% photosynthesis loss.",
            "severity": "medium",
            "symptoms": [
                "Silvery or brown serpentine mines on young leaves",
                "Blistered leaf surface",
                "Rolled or folded leaf tips",
                "Premature leaf drop in severe cases",
            ],
            "preventive_measures": [
                "Remove and destroy mined leaves regularly",
                "Apply systemic insecticide at flush emergence",
                "Monitor new flush growth closely",
                "Use light traps to monitor adult moth populations",
            ],
        },
        "cashew red rust": {
            "cause": "Cephaleuros virescens (algal leaf spot / red rust)",
            "remedy": "Apply Copper oxychloride (3g/L). Improve orchard ventilation by pruning.",
            "impact": "Premature defoliation and reduced photosynthesis in humid areas.",
            "severity": "medium",
            "symptoms": [
                "Rust-coloured velvety spots on upper leaf surface",
                "Spots with golden-orange sporangia",
                "Severe in high rainfall, shaded canopy",
                "Defoliation in chronic infections",
            ],
            "preventive_measures": [
                "Prune for open canopy to reduce humidity",
                "Apply copper spray before and during rains",
                "Remove and burn fallen infected leaves",
                "Avoid planting in poorly drained low-lying areas",
            ],
        },
    },

    # ─────────────────────────────── CHERRY ──────────────────────────────
    "cherry": {
        "cherry brown_spot": {
            "cause": "Blumeriella jaapii (Cherry leaf spot fungus)",
            "remedy": "Apply Captan or Ferbam. Rake and destroy fallen leaves to eliminate inoculum.",
            "impact": "Premature defoliation weakens trees and reduces next-year flower bud formation.",
            "severity": "medium",
            "symptoms": [
                "Purple-red circular spots on upper leaf surface",
                "White spore masses on lower surface",
                "Shot-hole appearance as lesion centres fall out",
                "Severe early defoliation in July–August",
            ],
            "preventive_measures": [
                "Rake and destroy all fallen leaves in autumn",
                "Apply fungicide from petal fall to harvest",
                "Plant resistant sweet cherry varieties",
                "Prune for open canopy to reduce humidity",
            ],
        },
        "cherry leaf scorch": {
            "cause": "Xanthomonas arboricola pv. pruni (Bacterial canker/shot hole)",
            "remedy": "Apply copper hydroxide at leaf fall. Prune affected branches.",
            "impact": "Reduced leaf area and premature defoliation; weakens tree.",
            "severity": "medium",
            "symptoms": [
                "Irregular brown necrotic areas on leaf margins",
                "Scorched appearance to leaf edges",
                "Premature defoliation in summer",
                "Gummosis on affected twigs",
            ],
            "preventive_measures": [
                "Apply protective copper spray at bud burst",
                "Avoid overhead irrigation",
                "Prune during dry weather",
                "Plant in well-drained sites with good air movement",
            ],
        },
        "cherry normal leaf": {
            "cause": "None",
            "remedy": "Continue potassium and calcium foliar application. Monitor for cherry fruit fly.",
            "impact": "Healthy tree — good fruit set expected.",
            "severity": "healthy",
            "symptoms": [],
            "preventive_measures": ["Continue balanced nutrition and regular pruning"],
        },
        "cherry purple leaf spot": {
            "cause": "Apiognomonia erythrostoma (Cherry leaf scorch fungus)",
            "remedy": "Apply Thiophanate-methyl or Mancozeb. Remove fallen leaves.",
            "impact": "Chronic defoliation reduces carbohydrate reserves and weakens trees.",
            "severity": "medium",
            "symptoms": [
                "Small purplish-red spots on leaves",
                "Spots may have tan centre as they age",
                "Spots coalesce causing large necrotic areas",
                "Early leaf drop in summer",
            ],
            "preventive_measures": [
                "Apply protective fungicide from petal fall",
                "Collect and burn all fallen leaves",
                "Maintain orchard hygiene",
                "Avoid dense canopy through annual pruning",
            ],
        },
        "cherry_shot hole disease": {
            "cause": "Coryneum blight / Stigmina carpophila",
            "remedy": "Apply Copper fungicide at leaf fall and green tip. Destroy pruned debris.",
            "impact": "Twig dieback and reduced cropping; severe in wet springs.",
            "severity": "medium",
            "symptoms": [
                "Circular purple-red spots that develop tan centres",
                "Spots fall out creating shot-holes",
                "Gummy lesions on young twigs and buds",
                "Infected buds turn black and fail to open",
            ],
            "preventive_measures": [
                "Apply dormant copper spray",
                "Prune and burn all infected twigs",
                "Ensure good drainage around root zone",
                "Plant in sites with good air drainage",
            ],
        },
    },

    # ─────────────────────────────── CORN ────────────────────────────────
    "corn": {
        "corn fungal leaf": {
            "cause": "Exserohilum turcicum (Northern Corn Leaf Blight) or Bipolaris maydis",
            "remedy": "Apply Azoxystrobin or Propiconazole at VT/R1 stage. Plant resistant hybrids.",
            "impact": "20–50% yield loss if upper leaves are affected before grain fill.",
            "severity": "high",
            "symptoms": [
                "Long elliptical grey-green to tan lesions on leaves",
                "Lesions with wavy margins, 2–15cm long",
                "Severe upper canopy blighting",
                "Premature drying of leaves",
            ],
            "preventive_measures": [
                "Plant resistant or tolerant hybrid varieties",
                "Rotate with non-grass crops",
                "Residue management: bury or compost infected stalks",
                "Apply fungicide at early tassel stage",
            ],
        },
        "corn gray leaf spot": {
            "cause": "Cercospora zeae-maydis fungus",
            "remedy": "Apply Trifloxystrobin + Propiconazole fungicide. Use tolerant hybrids.",
            "impact": "Can cause 20–60% yield loss in susceptible varieties.",
            "severity": "high",
            "symptoms": [
                "Rectangular tan to grey lesions parallel to leaf veins",
                "Lesions surrounded by yellow halo",
                "Lesions limited to veins giving striated appearance",
                "Severe in warm, humid conditions",
            ],
            "preventive_measures": [
                "Plant GLS-resistant hybrids",
                "Minimum tillage to manage residue",
                "Avoid continuous corn cultivation",
                "Apply fungicide at tassel emergence if risk is high",
            ],
        },
        "corn holcus_ leaf spot": {
            "cause": "Pseudomonas syringae pv. syringae (Bacterial leaf spot)",
            "remedy": "Generally requires no treatment; avoid excess nitrogen and dense canopy.",
            "impact": "Minor impact; primarily cosmetic leaf spots.",
            "severity": "medium",
            "symptoms": [
                "Small circular to oval water-soaked spots",
                "Spots turn tan to white with dark margin",
                "More prominent after frost or storm damage",
                "Generally self-limiting",
            ],
            "preventive_measures": [
                "Avoid excessive nitrogen fertilisation",
                "Plant in well-drained soils",
                "Maintain plant spacing for airflow",
                "No specific chemical control usually needed",
            ],
        },
        "corn normal leaf": {
            "cause": "None",
            "remedy": "Continue split nitrogen application and sufficient irrigation at silking.",
            "impact": "Healthy canopy — maximum grain fill expected.",
            "severity": "healthy",
            "symptoms": [],
            "preventive_measures": ["Continue balanced nutrition and timely irrigation at silking"],
        },
    },

    # ─────────────────────────────── CUCUMBER ────────────────────────────
    "cucumber": {
        "anthracnose": {
            "cause": "Colletotrichum orbiculare fungus",
            "remedy": "Apply Chlorothalonil or Azoxystrobin. Remove infected vines.",
            "impact": "Severe fruit rotting; significant market loss.",
            "severity": "high",
            "symptoms": [
                "Water-soaked sunken lesions on fruit",
                "Dark brown to black circular spots on leaves",
                "Pink salmon-coloured spore masses in wet weather",
                "Defoliation and fruit rot",
            ],
            "preventive_measures": [
                "Use certified disease-free seed",
                "Rotate cucurbits with non-related crops",
                "Avoid overhead irrigation",
                "Apply preventive fungicide at fruiting",
            ],
        },
        "bacterial wilt": {
            "cause": "Erwinia tracheiphila (bacteria spread by cucumber beetles)",
            "remedy": "Control cucumber beetle vectors with Carbaryl. Remove wilted plants promptly.",
            "impact": "Plants collapse rapidly; no recovery once infected.",
            "severity": "high",
            "symptoms": [
                "Sudden wilting of individual runners",
                "Oozing sticky bacterial strands when stem is cut",
                "Entire plant wilts within days",
                "Green colour retained initially during wilt",
            ],
            "preventive_measures": [
                "Control cucumber beetle from seedling stage",
                "Use floating row covers early in season",
                "Remove and destroy wilted plants immediately",
                "Plant resistant or tolerant varieties",
            ],
        },
        "belly rot": {
            "cause": "Rhizoctonia solani soil-borne fungus",
            "remedy": "Improve drainage. Mulch vines. Apply Thiophanate-methyl to soil.",
            "impact": "Post-harvest rot; significant packing shed losses.",
            "severity": "medium",
            "symptoms": [
                "Brown water-soaked lesions on fruit touching soil",
                "Rapid progression to soft rot",
                "Web-like mycelium visible on affected area",
                "Internal discolouration of fruit flesh",
            ],
            "preventive_measures": [
                "Use straw mulch to keep fruit off soil",
                "Improve field drainage",
                "Avoid overhead irrigation",
                "Harvest frequently to minimise soil contact time",
            ],
        },
        "downy mildew": {
            "cause": "Pseudoperonospora cubensis (oomycete)",
            "remedy": "Apply Famoxadone + Cymoxanil or Metalaxyl. Improve airflow.",
            "impact": "Rapid defoliation; 30–80% yield loss if untreated.",
            "severity": "high",
            "symptoms": [
                "Angular yellow spots on upper leaf surface",
                "Purple-grey mould on leaf underside",
                "Rapid browning and collapse of leaves",
                "Severe spread during cool, humid weather",
            ],
            "preventive_measures": [
                "Use downy mildew resistant varieties",
                "Avoid late afternoon irrigation",
                "Apply systemic fungicide preventively",
                "Improve field ventilation and drainage",
            ],
        },
        "fresh cucumber": {
            "cause": "None",
            "remedy": "Maintain consistent soil moisture and calcium fertilisation for quality fruit.",
            "impact": "Healthy fruit — excellent market quality expected.",
            "severity": "healthy",
            "symptoms": [],
            "preventive_measures": ["Continue consistent drip irrigation and foliar calcium"],
        },
        "fresh leaf": {
            "cause": "None",
            "remedy": "Continue balanced nutrition programme. Scout weekly for pests.",
            "impact": "Healthy foliage — maximum photosynthesis and yield.",
            "severity": "healthy",
            "symptoms": [],
            "preventive_measures": ["Regular monitoring and balanced NPK application"],
        },
        "gummy stem blight": {
            "cause": "Didymella bryoniae (Phoma cucurbitacearum) fungus",
            "remedy": "Apply Thiophanate-methyl or Azoxystrobin. Remove infected vines and fruit.",
            "impact": "Crown rot kills plants; fruit lesions cause market loss.",
            "severity": "high",
            "symptoms": [
                "Water-soaked lesions on stems with tan centres",
                "Amber gummy exudate from stem cankers",
                "Circular brown spots with cream centre on leaves",
                "Crown rot and plant collapse",
            ],
            "preventive_measures": [
                "Use certified disease-free seed",
                "Apply seed treatment with Thiram",
                "Rotate with non-cucurbit crops for 2+ years",
                "Avoid surface wounds during cultivation",
            ],
        },
        "pythium fruit rot": {
            "cause": "Pythium aphanidermatum (water mould, soil-borne)",
            "remedy": "Apply Metalaxyl to soil. Improve drainage. Mulch fruit-bearing vines.",
            "impact": "Rapid fruit decay; severe in waterlogged conditions.",
            "severity": "high",
            "symptoms": [
                "Water-soaked lesions on blossom end or soil contact areas",
                "Rapid collapse and soft watery rot",
                "White cottony mycelium on affected fruit",
                "Damping-off of seedlings in severe cases",
            ],
            "preventive_measures": [
                "Ensure excellent field drainage",
                "Mulch vines to prevent soil splash",
                "Avoid planting in Pythium-infested soil",
                "Use Metalaxyl soil drench before planting in high-risk fields",
            ],
        },
    },

    # ─────────────────────────────── FIG ─────────────────────────────────
    "fig": {
        "fig blight_leaf disease": {
            "cause": "Botrytis cinerea (Grey Mould) under humid conditions",
            "remedy": "Apply Iprodione or Cyprodinil. Improve orchard ventilation.",
            "impact": "Fruit mummification and shoot dieback; up to 40% fruit loss.",
            "severity": "high",
            "symptoms": [
                "Grey fuzzy mould on leaves, shoots and fruit",
                "Brown water-soaked lesions that shrivel",
                "Blighted flower clusters",
                "Mummified fruit remaining on tree",
            ],
            "preventive_measures": [
                "Prune for open canopy ventilation",
                "Remove mummified fruit and infected shoots",
                "Apply fungicide at early fruit set",
                "Avoid overhead irrigation",
            ],
        },
        "fig brown spot": {
            "cause": "Cercospora fici or Phyllosticta spp.",
            "remedy": "Apply Copper oxychloride or Mancozeb. Improve drainage.",
            "impact": "Early defoliation reduces carbohydrate storage for next season.",
            "severity": "medium",
            "symptoms": [
                "Reddish-brown spots with yellow halo on leaves",
                "Spots enlarge and coalesce",
                "Premature defoliation in summer",
                "Reduced fruit quality on weakened trees",
            ],
            "preventive_measures": [
                "Remove and destroy fallen leaves",
                "Apply preventive copper spray after harvest",
                "Ensure good soil drainage",
                "Balanced NPK to maintain tree vigour",
            ],
        },
        "fig normal leaf": {
            "cause": "None",
            "remedy": "Continue potassium nutrition and regulated deficit irrigation to enhance fruit sugar.",
            "impact": "Healthy tree — premium fruit quality expected.",
            "severity": "healthy",
            "symptoms": [],
            "preventive_measures": ["Continue balanced nutrition and annual pruning"],
        },
        "fig_rust leaf": {
            "cause": "Phakopsora fici (Fig rust fungus)",
            "remedy": "Apply Propiconazole or Tebuconazole. Remove infected leaves.",
            "impact": "Premature defoliation reduces fruit size and quality.",
            "severity": "high",
            "symptoms": [
                "Bright yellow-orange pustules on leaf undersides",
                "Corresponding yellow spots on upper surface",
                "Severe defoliation in humid, rainy conditions",
                "Weakened tree with reduced fruiting next season",
            ],
            "preventive_measures": [
                "Apply protective fungicide before rainy season",
                "Remove and bury fallen infected leaves",
                "Plant in well-ventilated sites",
                "Avoid water stress which predisposes trees",
            ],
        },
    },

    # ─────────────────────────────── GRAPE ───────────────────────────────
    "grape": {
        "grape anthracnose leaf": {
            "cause": "Elsinoe ampelina (Bird's Eye Rot / Anthracnose fungus)",
            "remedy": "Apply Mancozeb or Copper at bud burst. Prune for open canopy.",
            "impact": "Sunken fruit lesions make grapes unmarketable; severe in wet years.",
            "severity": "high",
            "symptoms": [
                "Small sunken brown spots with grey centre on leaves",
                "Dark shot-holes in leaves",
                "Sunken circular 'bird's eye' lesions on fruit",
                "Lesions on young shoots and canes",
            ],
            "preventive_measures": [
                "Apply dormant lime-sulphur spray",
                "Prune and burn infected canes in winter",
                "Train vines for good air circulation",
                "Apply protective fungicide from bud burst",
            ],
        },
        "grape brown spot leaf": {
            "cause": "Pseudocercospora vitis (Leaf spot / Isariopsis Leaf Spot)",
            "remedy": "Apply Mancozeb or Copper oxychloride. Rake and destroy fallen leaves.",
            "impact": "Premature defoliation reduces grape sugar accumulation.",
            "severity": "medium",
            "symptoms": [
                "Irregular brown spots on upper leaf surface",
                "Dark brown to black spore masses on lower surface",
                "Early defoliation of basal leaves",
                "Weakening of vine for next season",
            ],
            "preventive_measures": [
                "Maintain open canopy by hedging",
                "Collect and bury fallen leaves",
                "Apply copper spray after harvest",
                "Avoid excess nitrogen that promotes dense canopy",
            ],
        },
        "grape downy mildew leaf": {
            "cause": "Plasmopara viticola (Grapevine Downy Mildew)",
            "remedy": "Apply Metalaxyl + Mancozeb or Fosetyl-Al. Remove infected shoots.",
            "impact": "Can destroy entire crop; one of the most damaging grape diseases.",
            "severity": "high",
            "symptoms": [
                "Oil spot (oily-looking yellow patches) on upper leaves",
                "White downy sporulation on lower leaf surface",
                "Affected berries shrivel and drop ('leather berry')",
                "Shoot and tendril browning and death",
            ],
            "preventive_measures": [
                "Apply preventive fungicide before first rainfall in spring",
                "Prune for maximum sunlight penetration",
                "Use drip rather than overhead irrigation",
                "Plant in sites with good air drainage",
            ],
        },
        "grape mites_leaf disease": {
            "cause": "Calepitrimerus vitis or Colomerus vitis (Grape Bud and Rust Mites)",
            "remedy": "Apply Abamectin or Wettable Sulphur at early bud swell. Repeat in 14 days.",
            "impact": "Distorted shoots and leaves; reduced fruit set on severely affected vines.",
            "severity": "medium",
            "symptoms": [
                "Leaf rolling or reddish-bronze discolouration",
                "Galls or felt-like patches (erineum) on leaf underside",
                "Stunted and distorted young shoots",
                "Tiny mites visible with hand lens",
            ],
            "preventive_measures": [
                "Apply dormant oil or sulphur spray at tight cluster",
                "Avoid moving infested plant material",
                "Encourage natural predatory mites",
                "Remove severely affected buds in winter pruning",
            ],
        },
        "grape normal_leaf": {
            "cause": "None",
            "remedy": "Apply potassium and zinc foliar nutrition. Maintain leaf-to-fruit ratio.",
            "impact": "Healthy vine — optimum fruit quality and yield expected.",
            "severity": "healthy",
            "symptoms": [],
            "preventive_measures": ["Continue balanced nutrition and shoot positioning"],
        },
        "grape powdery_mildew leaf": {
            "cause": "Erysiphe necator (Uncinula necator) — Powdery Mildew",
            "remedy": "Apply Myclobutanil or Wettable Sulphur. Repeat every 14 days during risk periods.",
            "impact": "Berries crack and are prone to secondary rot; up to 80% quality loss.",
            "severity": "high",
            "symptoms": [
                "White powdery coating on green tissues",
                "Stunted and distorted shoots",
                "Russet net-like patterns on maturing berries",
                "Cracking of berries exposing seeds",
            ],
            "preventive_measures": [
                "Apply sulphur sprays from 5-leaf stage",
                "Maintain open canopy with leaf removal",
                "Avoid excess nitrogen",
                "Use tolerant varieties where available",
            ],
        },
        "grape shot hole leaf disease": {
            "cause": "Elsinoe ampelina secondary infection or nutrient deficiency",
            "remedy": "Apply copper-based fungicide. Correct potassium deficiency if present.",
            "impact": "Defoliation reduces sugar accumulation in berries.",
            "severity": "medium",
            "symptoms": [
                "Small spots that fall out leaving holes in leaves",
                "Yellow border around holes",
                "Primarily affects older leaves",
                "Associated with wet conditions early in season",
            ],
            "preventive_measures": [
                "Apply copper spray at bud burst",
                "Ensure balanced potassium nutrition",
                "Maintain good orchard hygiene",
                "Monitor and control early-season fungal diseases",
            ],
        },
    },

    # ─────────────────────────────── LYCHEE ──────────────────────────────
    "lychee": {
        "algal spot indirect": {
            "cause": "Cephaleuros virescens (Algal Leaf Spot)",
            "remedy": "Apply Copper oxychloride (3g/L). Prune for improved canopy ventilation.",
            "impact": "Weakens leaves and reduces photosynthesis in shaded conditions.",
            "severity": "medium",
            "symptoms": [
                "Rusty-red velvety spots on leaf surface",
                "Raised algal growth visible in humid weather",
                "Spotting more severe on lower, shaded leaves",
                "Chronic infections weaken older trees",
            ],
            "preventive_measures": [
                "Prune to open canopy and improve light penetration",
                "Apply copper spray before monsoon",
                "Remove and burn severely infected branches",
                "Maintain good orchard hygiene",
            ],
        },
        "anthracnose cloudy": {
            "cause": "Colletotrichum gloeosporioides (Anthracnose in cloudy/humid conditions)",
            "remedy": "Apply Carbendazim or Azoxystrobin. Remove infected tissue immediately.",
            "impact": "Fruit rot and flower blighting; severe in post-harvest handling.",
            "severity": "high",
            "symptoms": [
                "Brown circular spots on leaves with irregular margins",
                "Salmon-coloured spore masses in humid weather",
                "Blossom blighting reducing fruit set",
                "Post-harvest fruit rot during storage",
            ],
            "preventive_measures": [
                "Apply pre-harvest fungicide at fruit colouring",
                "Harvest at correct maturity to avoid post-harvest losses",
                "Cool storage at 4°C after harvest",
                "Maintain orchard sanitation",
            ],
        },
        "dry leaves": {
            "cause": "Physiological drought stress or salt toxicity",
            "remedy": "Improve irrigation management. Apply foliar potassium spray. Check soil EC.",
            "impact": "Reduces fruit quality and quantity in subsequent seasons.",
            "severity": "medium",
            "symptoms": [
                "Leaf tip and margin browning (scorch)",
                "Dry papery leaf texture",
                "Progressive browning from leaf tip downward",
                "Associated with drought, salt stress or root damage",
            ],
            "preventive_measures": [
                "Maintain consistent irrigation, especially at fruit fill",
                "Test soil and water EC annually",
                "Apply mulch to conserve soil moisture",
                "Avoid excess potassium or sodium fertilisation",
            ],
        },
        "entomosporium spot": {
            "cause": "Entomosporium maculatum fungal leaf spot",
            "remedy": "Apply Mancozeb or Copper fungicide. Remove infected leaves.",
            "impact": "Defoliation reduces tree vigour and next season productivity.",
            "severity": "medium",
            "symptoms": [
                "Small circular red spots on young leaves",
                "Spots develop dark fruiting bodies in the centre",
                "Young, rapidly expanding leaves most susceptible",
                "Infected leaves drop prematurely",
            ],
            "preventive_measures": [
                "Protect new flushes with fungicide spray",
                "Remove and destroy fallen infected leaves",
                "Avoid high-nitrogen fertilisation that promotes tender flushes",
                "Improve canopy ventilation",
            ],
        },
        "leaf mites direct": {
            "cause": "Aceria litchii (Lychee Erinose Mite) — direct infestation",
            "remedy": "Apply Abamectin (0.5 ml/L) or Wettable Sulphur. Repeat every 15 days.",
            "impact": "Severe new-growth distortion; 30–50% crop loss in infested orchards.",
            "severity": "high",
            "symptoms": [
                "Velvety brown erineum galls on lower leaf surface",
                "Distorted, blistered young leaves and shoots",
                "Flower and fruit infested with erinose",
                "Tiny mites visible under magnification",
            ],
            "preventive_measures": [
                "Apply Wettable Sulphur at bud break as preventive",
                "Prune and burn infested new flushes",
                "Avoid introducing planting material from infested orchards",
                "Conserve predatory mites by avoiding broad-spectrum pesticides",
            ],
        },
        "mayetiola postrain": {
            "cause": "Post-rain physiological disorder / Gall midge (Mayetiola sp.)",
            "remedy": "Apply Chlorpyrifos or Imidacloprid at new flush emergence. Remove galled leaves.",
            "impact": "New flush damage reduces fruiting potential for current season.",
            "severity": "medium",
            "symptoms": [
                "Rolled or folded young leaves with gall insect inside",
                "Yellowing and distortion of new flush growth",
                "Small orange-yellow larvae visible inside galls",
                "Severity increases after monsoon rains",
            ],
            "preventive_measures": [
                "Apply systemic insecticide at first flush after rain",
                "Remove and destroy galled plant parts",
                "Monitor flush emergence carefully after rains",
                "Maintain tree vigour through balanced nutrition",
            ],
        },
    },

    # ─────────────────────────────── RADISH ──────────────────────────────
    "radish": {
        "black leaf spot": {
            "cause": "Alternaria brassicae or Cercospora raphani fungus",
            "remedy": "Apply Mancozeb or Iprodione. Improve drainage and plant spacing.",
            "impact": "Reduces leaf quality and root yield in seed crop.",
            "severity": "medium",
            "symptoms": [
                "Dark brown to black circular spots on leaves",
                "Spots with yellow halo; centres may fall out",
                "Severe defoliation in high humidity",
                "Root surface darkening in severe cases",
            ],
            "preventive_measures": [
                "Treat seed with Thiram before planting",
                "Maintain plant spacing for good airflow",
                "Apply copper spray prophylactically",
                "Rotate with non-cruciferous crops",
            ],
        },
        "downey mildew": {
            "cause": "Peronospora parasitica (Crucifer Downy Mildew)",
            "remedy": "Apply Metalaxyl + Mancozeb. Improve field ventilation. Reduce leaf wetness.",
            "impact": "Defoliation and poor root development; up to 30% market loss.",
            "severity": "medium",
            "symptoms": [
                "Yellow irregular spots on upper leaf surface",
                "White downy sporulation on lower surface",
                "Leaves turn brown and papery in severe cases",
                "Cool, humid conditions favour spread",
            ],
            "preventive_measures": [
                "Plant in well-drained fields",
                "Avoid overhead irrigation in evenings",
                "Use disease-resistant radish varieties",
                "Apply protective fungicide at first sign",
            ],
        },
        "flea beetle": {
            "cause": "Phyllotreta striolata (Striped Flea Beetle) — insect feeding damage",
            "remedy": "Apply Spinosad or Deltamethrin. Use kaolin clay as physical repellent.",
            "impact": "Seedling stand loss in severe attacks; reduces young plant vigour.",
            "severity": "medium",
            "symptoms": [
                "Numerous small round holes in young leaves",
                "Shotgun-like pitting pattern on leaf surface",
                "Seedlings severely stunted when heavily attacked",
                "Beetles visible and jump when disturbed",
            ],
            "preventive_measures": [
                "Use floating row covers to protect seedlings",
                "Plant later in season when beetle populations lower",
                "Apply kaolin clay barrier spray",
                "Rotate planting locations each season",
            ],
        },
        "fresh leaf": {
            "cause": "None",
            "remedy": "Continue consistent irrigation and balanced calcium nitrate nutrition.",
            "impact": "Healthy foliage — optimal root development expected.",
            "severity": "healthy",
            "symptoms": [],
            "preventive_measures": ["Maintain consistent irrigation and nutrition programme"],
        },
        "mosaic virus": {
            "cause": "Turnip Mosaic Virus (TuMV) transmitted by aphids",
            "remedy": "Control aphid vectors with Imidacloprid. Remove infected plants. Use reflective mulch.",
            "impact": "Mosaic pattern on leaves; reduced root size and quality.",
            "severity": "high",
            "symptoms": [
                "Yellow-green mosaic mottling on leaves",
                "Leaf distortion and stunting",
                "Thickened, lumpy root surface",
                "Severely reduced root marketability",
            ],
            "preventive_measures": [
                "Control aphid populations early with systemic insecticide",
                "Remove and destroy infected plants immediately",
                "Use reflective mulch to deter aphid landing",
                "Eliminate weed reservoirs near planting areas",
            ],
        },
    },

    # ─────────────────────────────── WALNUT ──────────────────────────────
    "walnut": {
        "walnut anthracnose_leaf disease": {
            "cause": "Ophiognomonia leptostyla (Marssonina walnut blight)",
            "remedy": "Apply Mancozeb or Copper fungicide. Rake and destroy fallen leaves.",
            "impact": "Premature defoliation reduces kernel filling; up to 30% yield loss.",
            "severity": "high",
            "symptoms": [
                "Brown circular spots with dark border on leaves",
                "Spots coalesce causing large necrotic patches",
                "Premature leaf and nut drop",
                "Severe in wet summers",
            ],
            "preventive_measures": [
                "Collect and burn all fallen leaves in autumn",
                "Apply copper spray at bud burst",
                "Prune for open canopy to reduce humidity",
                "Use resistant walnut varieties where available",
            ],
        },
        "walnut blotch_leaf disease": {
            "cause": "Microstroma juglandis fungus (White Mould / Downy Leaf Spot)",
            "remedy": "Apply Mancozeb at first symptom. Improve canopy ventilation.",
            "impact": "Defoliation reduces tree vigour and next-season production.",
            "severity": "medium",
            "symptoms": [
                "White powdery blotches on lower leaf surface",
                "Corresponding yellow areas on upper surface",
                "Early defoliation in wet summers",
                "More severe on young, vigorous trees",
            ],
            "preventive_measures": [
                "Prune for open canopy structure",
                "Apply copper spray preventively before rains",
                "Remove fallen leaves promptly",
                "Maintain balanced nitrogen nutrition",
            ],
        },
        "walnut leaf gall mite": {
            "cause": "Aceria erinea (Walnut Eriophyid Mite) — gall-forming",
            "remedy": "Apply Abamectin or Wettable Sulphur at bud burst. Repeat every 15–21 days.",
            "impact": "Cosmetic galling; severe in young trees — can reduce leaf area.",
            "severity": "medium",
            "symptoms": [
                "Brown felt-like erineum galls on leaf undersides",
                "Raised blistered patches on upper surface",
                "Heavy infestation causes leaf distortion",
                "Tiny mites visible inside galls with hand lens",
            ],
            "preventive_measures": [
                "Apply dormant oil spray in late winter",
                "Prune and burn heavily galled shoots",
                "Avoid broad-spectrum pesticides that harm predatory mites",
                "Monitor young tree flushes closely in spring",
            ],
        },
        "walnut normal_leaf": {
            "cause": "None",
            "remedy": "Continue zinc and boron micronutrient foliar sprays. Maintain weed-free basin.",
            "impact": "Healthy tree — premium kernel quality and yield expected.",
            "severity": "healthy",
            "symptoms": [],
            "preventive_measures": ["Continue balanced nutrition and regular pruning"],
        },
        "walnut shot_hole": {
            "cause": "Xanthomonas arboricola pv. juglandis (Walnut Blight bacterium)",
            "remedy": "Apply Copper bactericide at bud burst and again 10 days later.",
            "impact": "Nut blight causes dark shrivelled kernels; up to 50% loss in wet springs.",
            "severity": "high",
            "symptoms": [
                "Small dark spots with water-soaked margin on leaves",
                "Spots dry and fall out creating shot-holes",
                "Black sunken lesions on green nuts",
                "Blackening of nut kernels (walnut blight)",
            ],
            "preventive_measures": [
                "Apply copper spray at 5% and 50% bud burst",
                "Prune for open canopy to improve drying",
                "Remove and destroy mummified nuts",
                "Plant resistant or less-susceptible varieties",
            ],
        },
    },
}


def get_disease_info(crop: str, disease: str) -> DiseaseEntry:
    """
    Return disease information for a given crop and disease name.
    Performs case-insensitive lookup.
    Returns a default entry if not found.
    """
    crop_db = AGRI_DATABASE.get(crop.lower(), {})
    # Try exact match first, then case-insensitive
    info = crop_db.get(disease.lower()) or crop_db.get(disease)
    if info is None:
        return DiseaseEntry(
            cause="Biological analysis pending.",
            remedy=KVK_DEFAULT_REMEDY,
            impact="Consult a local agronomist for economic impact assessment.",
            severity="medium",
            symptoms=[],
            preventive_measures=[KVK_DEFAULT_REMEDY],
        )
    return info
