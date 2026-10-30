# Krishika AI — MongoDB Database Architecture & Design (CSE494)

## Course Submission
- **Course**: CSE494 — Intelligent NoSQL Databases (MongoDB)
- **Database System**: MongoDB 6.0+ (NoSQL Document Store)
- **Database Name**: `krishika_cse494`
- **Application**: Krishika AI Crop Disease Detection & Agricultural Advisory System

---

## 1. Architectural Philosophy: Document Model in Agriculture

In traditional relational databases (RDBMS), an agricultural diagnosis requires multiple tables (`detections`, `diagnoses`, `treatments`, `symptoms`, `preventative_measures`) connected through heavy foreign key joins. In agricultural diagnostics, real-time performance and audit immutability are critical: when a diagnosis is produced, the recommended remedy and symptoms should be stored directly with the diagnosis document at that snapshot in time.

### Normalization vs. Denormalization Decision Matrix

| Entity | Schema Strategy | Technical Rationale |
| :--- | :--- | :--- |
| **`detections.diagnosis`** | **Embedded Document** (Denormalized) | **Atomic Read & Zero-Join Latency**: High read frequency; when a farmer or agronomist views a diagnosis, all treatment details, symptoms, and severity must be fetched in a single document read. Also preserves historical immutability if future treatments change. |
| **`crops.growing_information`** | **Embedded Document** (Denormalized) | **Strong 1-to-1 Domain Coupling**: Soil types, rainfall, temperature, and harvesting seasons are intrinsic attributes of the crop species. |
| **`crops` ↔ `diseases`** | **Referenced Collection** (`$lookup` Join) | **Many-to-Many & Dynamic Updates**: Pathogen descriptions and scientific taxonomies are managed globally across crop varieties and require cross-collection aggregation via `$lookup`. |
| **`farmers` ↔ `detections`** | **Referenced Collection** (Normalized) | **Unbounded Growth**: A farmer may generate hundreds of scans over years. Embedding detections inside farmer documents would violate MongoDB's 16MB document size limit (Anti-Pattern: Large Arrays). |

---

## 2. Collection Schemas & `$jsonSchema` Validation

The database enforces document integrity using MongoDB `$jsonSchema` validators on collection creation.

### 2.1 Collection: `farmers`
Stores registered farmer profiles, location metadata, and embedded aggregate counters.

```javascript
{
  $jsonSchema: {
    bsonType: "object",
    required: ["phone", "password_hash", "created_at"],
    properties: {
      _id: { bsonType: "objectId" },
      phone: {
        bsonType: "string",
        pattern: "^[0-9]{10}$",
        description: "10-digit Indian mobile number"
      },
      password_hash: { bsonType: "string" },
      full_name: { bsonType: "string" },
      email: { bsonType: "string" },
      state: { bsonType: "string" },
      district: { bsonType: "string" },
      crops_grown: {
        bsonType: "array",
        items: { bsonType: "string" }
      },
      stats: {
        bsonType: "object",
        properties: {
          total_detections: { bsonType: "int" },
          last_detection_at: { bsonType: "date" }
        }
      },
      created_at: { bsonType: "date" },
      updated_at: { bsonType: "date" }
    }
  }
}
```

### 2.2 Collection: `detections`
Stores inference results from the VGG19 + SVM pipeline with embedded diagnosis sub-documents.

```javascript
{
  $jsonSchema: {
    bsonType: "object",
    required: ["crop", "disease", "confidence", "created_at"],
    properties: {
      _id: { bsonType: "objectId" },
      farmer_id: { bsonType: ["objectId", "null"] },
      crop: { bsonType: "string" },
      disease: { bsonType: "string" },
      confidence: { bsonType: "double", minimum: 0.0, maximum: 1.0 },
      is_uncertain: { bsonType: "bool" },
      image_filename: { bsonType: ["string", "null"] },
      image_path: { bsonType: ["string", "null"] },
      diagnosis: {
        bsonType: "object",
        required: ["severity", "remedy"],
        properties: {
          severity: { enum: ["Low", "Medium", "High", "Critical"] },
          remedy: { bsonType: "string" },
          cause: { bsonType: "string" },
          impact: { bsonType: "string" },
          symptoms: { bsonType: "array", items: { bsonType: "string" } },
          preventive_measures: { bsonType: "array", items: { bsonType: "string" } }
        }
      },
      created_at: { bsonType: "date" }
    }
  }
}
```

### 2.3 Collection: `crops`
Stores crop species information with embedded growing parameters.

```javascript
{
  $jsonSchema: {
    bsonType: "object",
    required: ["crop_id", "name", "created_at"],
    properties: {
      _id: { bsonType: "objectId" },
      crop_id: { bsonType: "string" },
      name: { bsonType: "string" },
      scientific_name: { bsonType: "string" },
      family: { bsonType: "string" },
      growing_information: {
        bsonType: "object",
        properties: {
          optimal_temp_celsius: { bsonType: "string" },
          rainfall_mm: { bsonType: "string" },
          soil_type: { bsonType: "string" },
          sowing_season: { bsonType: "string" },
          harvest_duration_days: { bsonType: "string" }
        }
      },
      economic_importance: { bsonType: "string" },
      created_at: { bsonType: "date" }
    }
  }
}
```

### 2.4 Collection: `diseases`
Stores independent disease definitions referenced by `crop_id`.

```javascript
{
  $jsonSchema: {
    bsonType: "object",
    required: ["crop_id", "disease_name", "severity"],
    properties: {
      _id: { bsonType: "objectId" },
      crop_id: { bsonType: "string" },
      disease_name: { bsonType: "string" },
      pathogen_type: { bsonType: "string" },
      severity: { enum: ["Low", "Medium", "High", "Critical"] },
      remedy: { bsonType: "string" },
      cause: { bsonType: "string" },
      impact: { bsonType: "string" },
      symptoms: { bsonType: "array", items: { bsonType: "string" } },
      preventive_measures: { bsonType: "array", items: { bsonType: "string" } },
      created_at: { bsonType: "date" }
    }
  }
}
```

---

## 3. Indexing Strategy & Query Optimization

To maintain sub-millisecond query latency and avoid full collection scans (`COLLSCAN`), indexes are configured on high-cardinality and filter fields:

| Collection | Index Key | Index Type | Query Optimization Target |
| :--- | :--- | :--- | :--- |
| `farmers` | `{ phone: 1 }` | **Unique** | O(1) B-tree lookup on login and registration duplicate prevention |
| `detections` | `{ farmer_id: 1, created_at: -1 }` | **Compound** | Paginated scan history filtered by authenticated farmer sorted by newest first |
| `detections` | `{ crop: 1, "diagnosis.severity": 1 }` | **Compound** | Analytics aggregation and crop vulnerability filtering |
| `detections` | `{ created_at: -1 }` | **Single-Field** | Global audit feeds and temporal aggregation pipelines |
| `crops` | `{ crop_id: 1 }` | **Unique** | Primary identifier for joining with diseases |
| `diseases` | `{ crop_id: 1, disease_name: 1 }` | **Compound Unique** | Fast resolution during `$lookup` stages |

---

## 4. Complex MongoDB Aggregation Pipelines

### Pipeline 1: Global Multi-Faceted Analytics (`$facet`)
Aggregates summary counts, severity ratios, and most vulnerable crops in a single database invocation.

```python
pipeline = [
    {
        "$facet": {
            "summary": [
                {
                    "$group": {
                        "_id": None,
                        "total_scans": {"$sum": 1},
                        "avg_confidence": {"$avg": "$confidence"},
                        "high_severity_count": {
                            "$sum": {
                                "$cond": [
                                    {"$in": ["$diagnosis.severity", ["High", "Critical"]]},
                                    1,
                                    0
                                ]
                            }
                        }
                    }
                }
            ],
            "severity_breakdown": [
                {"$group": {"_id": "$diagnosis.severity", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ],
            "top_crops": [
                {"$group": {"_id": "$crop", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 6}
            ]
        }
    }
]
```

### Pipeline 2: Temporal Trends (`$group` + `$dateToString`)
Tracks monthly disease spikes to alert regional agricultural officers.

```python
pipeline = [
    {
        "$group": {
            "_id": {
                "$dateToString": {"format": "%Y-%m", "date": "$created_at"}
            },
            "total_detections": {"$sum": 1},
            "high_severity_alerts": {
                "$sum": {
                    "$cond": [{"$eq": ["$diagnosis.severity", "High"]}, 1, 0]
                }
            }
        }
    },
    {"$sort": {"_id": 1}}
]
```

### Pipeline 3: Cross-Collection Join (`$lookup`)
Joins `crops` with `diseases` on `crop_id`.

```python
pipeline = [
    {"$match": {"crop_id": crop_id}},
    {
        "$lookup": {
            "from": "diseases",
            "localField": "crop_id",
            "foreignField": "crop_id",
            "as": "associated_diseases"
        }
    },
    {
        "$project": {
            "name": 1,
            "scientific_name": 1,
            "growing_information": 1,
            "associated_diseases": 1,
            "total_pathogens": {"$size": "$associated_diseases"}
        }
    }
]
```
