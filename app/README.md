# Insurance Claims Processing Application

AI-powered insurance claims processing system built with Python Flask and AWS Bedrock.

## 🚀 Quick Start

### With Observability (Recommended)

```bash
# From project root
python start_all.py

# Or manually:
cd observability && python start_observability.py
cd ../app && python app_instrumented.py
```

### Basic App Only

```bash
cd app
python app.py
```

## 📁 App Structure

```
app/
├── app.py                   # Basic Flask application
├── app_instrumented.py      # Flask app with observability
├── run.py                   # App startup script
├── deploy.py                # AWS deployment script
├── requirements.txt         # Python dependencies
├── templates/               # HTML templates
│   └── index.html
├── lambda/                  # Lambda functions
│   └── claims_processor.py
└── infrastructure/          # AWS CDK infrastructure
    ├── app.py
    ├── cdk.json
    └── requirements.txt
```

## 🔧 Configuration

1. **Copy environment template:**
   ```bash
   cp env.example .env
   ```

2. **Edit .env with your AWS credentials:**
   ```env
   AWS_REGION=us-east-1
   AWS_ACCESS_KEY_ID=your_key
   AWS_SECRET_ACCESS_KEY=your_secret
   S3_BUCKET_NAME=your_bucket
   # ... other config
   ```

## 🚀 Deployment

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Start the app
python app.py
# or
python app_instrumented.py  # with observability
```

### AWS Deployment

```bash
# Deploy infrastructure
python deploy.py

# Or manually:
cd infrastructure
pip install -r requirements.txt
cdk bootstrap
cdk deploy
```

## 📊 Features

- **AI-Powered Claims Processing** - Uses AWS Bedrock Claude models
- **Document Upload** - Support for images and PDFs
- **Real-time Chat** - Interactive AI assistant
- **Status Tracking** - Real-time claim monitoring
- **Observability** - Full monitoring and tracing (when using app_instrumented.py)

## 🔍 API Endpoints

- `GET /` - Main application interface
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics (instrumented version)
- `POST /api/claims/submit` - Submit new claim
- `GET /api/claims/<id>` - Get claim status
- `POST /api/chat` - Chat with AI assistant

## 🛠️ Development

### Adding New Features

1. **Add new routes** in `app.py` or `app_instrumented.py`
2. **Update templates** in `templates/`
3. **Add Lambda functions** in `lambda/`
4. **Update infrastructure** in `infrastructure/`

### Testing

```bash
# Test health endpoint
curl http://localhost:3000/health

# Test metrics (instrumented version)
curl http://localhost:3000/metrics

# Test claim submission
curl -X POST http://localhost:3000/api/claims/submit \
  -F "policyNumber=POL001" \
  -F "claimType=auto" \
  -F "description=Test claim" \
  -F "amount=1000" \
  -F "contactEmail=test@example.com"
```

## 🔧 Troubleshooting

### Common Issues

1. **AWS Credentials Not Found**
   ```bash
   aws configure
   ```

2. **Missing Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Port Already in Use**
   ```bash
   # Change port in .env
   PORT=3001
   ```

4. **S3 Bucket Not Found**
   - Create bucket in AWS Console
   - Update S3_BUCKET_NAME in .env

### Debug Mode

```bash
# Enable debug logging
export NODE_ENV=development
python app.py
```

## 📚 Documentation

- **Main Project**: See `../README.md`
- **Observability**: See `../observability/OBSERVABILITY.md`
- **Infrastructure**: See `infrastructure/` folder

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request
