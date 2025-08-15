# Machine Learning and Deep Learning Learning Project

This directory contains learning materials and examples for:
- Machine Learning fundamentals
- Deep Learning concepts and applications
- Practical projects combining ML/DL with trip planning

## Structure

- `notebooks/` - Jupyter notebooks with interactive examples
- `examples/` - Python example scripts
- `datasets/` - Sample datasets for learning
- `models/` - Trained model files
- `web/` - Web interface for online demonstration

## Getting Started

1. Install additional ML/DL requirements:
```bash
pip install -r learning_requirements.txt
```

2. Start Jupyter Lab:
```bash
jupyter lab learning/notebooks/
```

3. Open the web demo:
```bash
python -m http.server 8000
```
Then visit http://localhost:8000/learning/web/

## Learning Path

1. Start with basic ML concepts in `notebooks/01_ml_basics.ipynb`
2. Explore deep learning in `notebooks/02_dl_fundamentals.ipynb`
3. Apply concepts to trip planning in `notebooks/03_ml_for_trips.ipynb`
4. Try interactive examples in the web interface