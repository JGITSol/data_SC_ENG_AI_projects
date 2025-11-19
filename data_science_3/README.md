# NLP Sentiment Analysis API

![Complexity](https://img.shields.io/badge/Complexity-Advanced-orange)
![NLP](https://img.shields.io/badge/NLP-Transformers%20%7C%20BERT-blue)

Production-ready sentiment and emotion analysis API using state-of-the-art transformers.

---

## 🎯 Overview

Real-time NLP analysis using pre-trained transformer models:
- **Sentiment Analysis** - DistilBERT (fine-tuned on SST-2)
- **Emotion Detection** - DistilRoBERTa (7 emotions)
- **Fast Inference** - Optimized for production use

---

## 🚀 Quick Start

```bash
cd data_science_3
pip install -r requirements.txt
python -m src.main
```

Access API at `http://localhost:8083/docs`

---

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/analyze` | POST | Full analysis (sentiment + emotions) |
| `/sentiment` | POST | Sentiment only (faster) |
| `/emotions` | POST | Emotions only |
| `/analyze/batch` | POST | Batch processing (up to 100 texts) |
| `/health` | GET | Health check |

---

## 💡 Example Usage

```bash
# Sentiment analysis
curl -X POST "http://localhost:8083/analyze" \
  -H "Content-Type: application/json" \
  -d '{"text": "I love this product!"}'

# Response:
{
  "text": "I love this product!",
  "sentiment": {
    "label": "POSITIVE",
    "score": 0.9998
  },
  "emotions": [
    {"emotion": "joy", "score": 0.9245},
    {"emotion": "love", "score": 0.0532},
    {"emotion": "surprise", "score": 0.0123}
  ]
}
```

---

## 🧠 Models Used

1. **DistilBERT** (Sentiment)
   - 66M parameters
   - Fine-tuned on SST-2
   - 95% accuracy

2. **DistilRoBERTa** (Emotions)
   - 82M parameters
   - 7 emotion classes: joy, sadness, anger, fear, love, surprise, neutral

---

## 🛠️ Tech Stack

- **Transformers** - Hugging Face library
- **PyTorch** - Deep learning framework
- **FastAPI** - REST API
- **Pydantic** - Data validation

---

## 📊 Portfolio Value

✅ **NLP Expertise** - Transformers, BERT  
✅ **Production API** - FastAPI deployment  
✅ **Pre-trained Models** - Transfer learning  
✅ **Batch Processing** - Efficient inference  
✅ **Modern Stack** - State-of-the-art NLP

---

## 🎓 Skills Demonstrated

- Natural Language Processing
- Transformer architectures
- Transfer learning
- API design
- Model serving

---

## 📝 License

MIT
