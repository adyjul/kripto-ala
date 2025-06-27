import joblib

def save_model(model, path='model_scalping_15m.pkl'):
    joblib.dump(model, path)

def load_model(path='model_scalping_15m.pkl'):
    return joblib.load(path)