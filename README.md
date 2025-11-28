# 🚗 AI Car Inspector

An AI-powered low-code application that uses Google's Gemini 2.0 Flash to analyze car images and provide detailed information about make, model, year, and more. Built with Gradio, containerized with Docker, and deployed on Kubernetes.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Gradio](https://img.shields.io/badge/Gradio-4.44.0-orange)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![Kubernetes](https://img.shields.io/badge/Kubernetes-Ready-brightgreen)

## 🌟 Features

- ✅ **Car Detection**: Automatically identifies if uploaded image contains a car
- 🚗 **Detailed Analysis**: Extracts make, model, year, body type, color, and condition
- 🎨 **Minimal UI**: Clean, user-friendly Gradio interface
- 🐳 **Containerized**: Fully dockerized for easy deployment
- ☸️ **Kubernetes Ready**: Complete K8s manifests included
- 🔄 **CI/CD Pipeline**: Automated build and deployment with GitHub Actions
- 🤖 **AI-Powered**: Uses Gemini 2.0 Flash with optimized temperature settings

## 🏗️ Architecture

```
User Browser → Gradio UI (Port 7860) → Python Backend → Gemini 2.0 Flash API → Response
```

### Tech Stack
- **Frontend**: Gradio (Low-code UI framework)
- **Backend**: Python 3.11
- **AI Model**: Gemini 2.0 Flash (gemini-2.0-flash-exp)
- **Container**: Docker
- **Orchestration**: Kubernetes/OpenShift
- **CI/CD**: GitHub Actions
- **Registry**: Docker Hub

## 📋 Prerequisites

- Python 3.11+
- Docker
- Kubernetes cluster (or Minikube/OpenShift)
- Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))
- Docker Hub account
- kubectl configured

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/your-username/car-inspector.git
cd car-inspector
```

2. **Set up environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure API key**
```bash
cp .env.example .env
# Edit .env and add your Gemini API key
```

4. **Run the application**
```bash
python app.py
```

5. **Open browser**
```
http://localhost:7860
```

### Docker Deployment

1. **Build Docker image**
```bash
docker build -t car-inspector:latest .
```

2. **Run container**
```bash
docker run -p 7860:7860 -e GEMINI_API_KEY=your_api_key car-inspector:latest
```

3. **Access application**
```
http://localhost:7860
```

### Kubernetes Deployment

1. **Create secret with API key**
```bash
kubectl create secret generic car-inspector-secret \
  --from-literal=GEMINI_API_KEY=your_actual_api_key
```

2. **Update deployment image**
Edit `kubernetes/deployment.yaml` and replace `your-dockerhub-username` with your actual Docker Hub username.

3. **Apply Kubernetes manifests**
```bash
kubectl apply -f kubernetes/secret.yaml
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml
```

4. **Check deployment status**
```bash
kubectl get pods
kubectl get services
```

5. **Access application**
```bash
# For LoadBalancer
kubectl get service car-inspector-service

# For NodePort
kubectl get nodes -o wide
# Access at http://<node-ip>:30860
```

## 🔧 Configuration

### Hardcoded Settings
These settings are intentionally hardcoded for consistency:

```python
MODEL_NAME = "gemini-2.0-flash-exp"
TEMPERATURE = 0.4
```

### Environment Variables
- `GEMINI_API_KEY`: Your Gemini API key (required)

## 📁 Project Structure

```
car-inspector/
├── app.py                    # Main Gradio application
├── requirements.txt          # Python dependencies
├── Dockerfile               # Docker configuration
├── .dockerignore            # Docker ignore file
├── .env.example             # Environment template
├── README.md                # This file
├── kubernetes/
│   ├── deployment.yaml      # K8s deployment
│   ├── service.yaml         # K8s service
│   └── secret.yaml          # K8s secret template
├── .github/
│   └── workflows/
│       └── ci-cd.yaml       # CI/CD pipeline
└── capstone_reflection.md   # Project documentation
```

## 🔄 CI/CD Pipeline

The project includes a GitHub Actions workflow that:

1. **Builds and tests** the application
2. **Creates Docker image** with commit SHA and latest tags
3. **Pushes to Docker Hub**
4. **Deploys to Kubernetes** (manual trigger or automated)

### Setup GitHub Secrets

Add these secrets to your GitHub repository:
- `DOCKER_USERNAME`: Your Docker Hub username
- `DOCKER_PASSWORD`: Your Docker Hub password/token
- `KUBECONFIG`: Your Kubernetes config (optional, for auto-deployment)

## 🧪 Testing

### Test with Sample Images

1. **Upload a car image**: Should provide detailed analysis
2. **Upload a non-car image**: Should display warning message
3. **Test various car types**: Sedans, SUVs, trucks, sports cars
4. **Test edge cases**: Poor lighting, multiple cars, partial views

### Expected Output Example

```
✅ Car Detected Successfully!

🚗 AI Analysis Results:

- Make: Toyota
- Model: Camry
- Year: 2020-2023 (8th generation)
- Body Type: Sedan
- Color: Silver/Gray
- Condition: Excellent
- Features: LED headlights, modern design
- Facts: One of the best-selling sedans globally
```

## 📊 Monitoring

### Check Pod Health
```bash
kubectl get pods -w
kubectl logs -f deployment/car-inspector
```

### View Service Status
```bash
kubectl describe service car-inspector-service
```

### Resource Usage
```bash
kubectl top pods
```

## 🔒 Security

- API keys stored in Kubernetes Secrets
- No hardcoded credentials in code
- Environment variable injection
- Resource limits applied
- Regular security updates

## 🐛 Troubleshooting

### Common Issues

**1. Gradio not accessible in container**
- Ensure `server_name="0.0.0.0"` in app.py
- Check port 7860 is exposed

**2. Gemini API errors**
- Verify API key is correct
- Check API quota/rate limits
- Ensure internet connectivity

**3. Kubernetes pods not starting**
```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

**4. CI/CD pipeline failing**
- Check Docker Hub credentials
- Verify Dockerfile syntax
- Ensure all files are committed

## 📚 Documentation

- [Gradio Documentation](https://gradio.app/docs/)
- [Gemini API Documentation](https://ai.google.dev/docs)
- [Docker Documentation](https://docs.docker.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)

## 🤝 Team Contributions

- **Person 1**: Application development and AI integration
- **Person 2**: Containerization and CI/CD setup
- **Person 3**: Kubernetes deployment and documentation

## 📝 License

This project is for educational purposes as part of the DevOps Capstone project.

## 🙏 Acknowledgments

- Google Gemini API for AI capabilities
- Gradio for the low-code UI framework
- IBM Docker/Kubernetes course for guidance

## 📧 Contact

For questions or issues, please open an issue on GitHub.
#Done by Dev-Api-Org