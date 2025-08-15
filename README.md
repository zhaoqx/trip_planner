# Trip Planner & ML/DL Learning Project

This project combines intelligent trip planning with comprehensive Machine Learning and Deep Learning learning materials. It provides both practical travel planning functionality and educational resources for ML/DL concepts.

## 🎯 Project Features

### Travel Planning (Original)
- Scrapes data from multiple travel websites
- Generates personalized trip plans using AI
- Uses GitHub Copilot to assist in the planning process

### ML/DL Learning (New)
- Interactive Jupyter notebooks for hands-on learning
- Real-world applications using travel data
- Online demonstrations and visualizations
- Progressive learning path from basics to advanced concepts

## 🚀 Quick Start

### For Trip Planning
```bash
pip install -r requirements.txt
python main.py
```

### For ML/DL Learning
```bash
# Install ML/DL dependencies
pip install -r learning_requirements.txt

# Start Jupyter Lab
jupyter lab learning/notebooks/

# Or view online demo
python -m http.server 8000
# Visit: http://localhost:8000/learning/web/
```

## 📚 Learning Resources

- **[Online Demo](https://zhaoqx.github.io/trip_planner/)** - GitHub Pages demonstration
- **`learning/notebooks/`** - Interactive Jupyter notebooks
- **`learning/examples/`** - Python example scripts
- **`learning/web/`** - Web-based demonstrations

## 🧠 Learning Path

1. **ML Basics** - Linear regression, classification, clustering
2. **Deep Learning** - Neural networks, CNN, RNN
3. **Applications** - Recommendation systems, NLP, optimization
4. **Projects** - Build real-world travel AI applications

## 📁 Project Structure

```
trip_planner/
├── learning/                 # ML/DL learning materials
│   ├── notebooks/           # Jupyter notebooks
│   ├── examples/            # Python examples
│   ├── web/                 # Online demonstrations
│   └── datasets/            # Sample datasets
├── scrapers/                # Travel data scrapers
├── planners/                # Trip planning logic
├── tools/                   # Utilities and tools
└── docs/                    # Documentation
```

## 🌐 Online Demo

Visit the [GitHub Pages site](https://zhaoqx.github.io/trip_planner/) to see interactive demonstrations of:
- Tourist attraction recommendation system
- Sentiment analysis of travel reviews
- Route optimization algorithms
- Data visualization dashboards

## 🛠️ Installation

1. Clone the repository
2. Install base requirements: `pip install -r requirements.txt`
3. Install ML/DL requirements: `pip install -r learning_requirements.txt`
4. Set up API keys in `config.py` (for travel features)

## 📖 Usage

### Travel Planning
Run the main application and follow the prompts:
```bash
python main.py
```

### Learning ML/DL
Start with the first notebook:
```bash
jupyter lab learning/notebooks/01_ml_basics.ipynb
```

### Web Demonstrations
Launch local server and explore:
```bash
cd learning/web && python -m http.server 8000
```

## 🤝 Contributing

This project welcomes contributions to both travel planning features and learning materials. Please see the documentation for guidelines.

## 📄 License

MIT License - feel free to use this project for learning and development.

---

**Note**: This project serves dual purposes - practical travel planning and ML/DL education. Choose the features that match your interests!
