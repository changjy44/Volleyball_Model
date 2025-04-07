import numpy as np
from sklearn.multioutput import MultiOutputRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression

class LinearModel:
    def __init__(self):
        pass
    
    def fit_attack(self, attack, block_dig):
        attack_data = np.array(attack)
        block_data = np.array(block_dig)
        attack_scaler = StandardScaler()
        block_dig_scaler = StandardScaler()
        Y_scaled = attack_scaler.fit_transform(attack_data)
        X_scaled = block_dig_scaler.fit_transform(block_data)
        
        attack_model = MultiOutputRegressor(LinearRegression())
        attack_model.fit(X_scaled, Y_scaled)
        
        self.attack_scaler = attack_scaler
        self.block_dig_scaler = block_dig_scaler
        self.attack_model = attack_model

    
    def fit_service(self, service, reception):
        service_data = np.array(service)
        reception_data = np.array(reception)
        service_scaler = StandardScaler()
        reception_scaler = StandardScaler()
        Y_scaled = service_scaler.fit_transform(service_data)
        X_scaled = reception_scaler.fit_transform(reception_data)
        
        service_model = MultiOutputRegressor(LinearRegression())
        service_model.fit(X_scaled, Y_scaled)
        
        self.service_scaler = service_scaler
        self.reception_scaler = reception_scaler
        self.service_model = service_model
    
    def predict_attack(self, block_dig):
        block_data = np.array([block_dig])
        X_scaled = self.block_dig_scaler.transform(block_data)
        prediction = self.attack_model.predict(X_scaled)
        Y_unscaled = self.attack_scaler.inverse_transform(prediction)
        return Y_unscaled
    
    def predict_service(self, reception):
        reception_data = np.array([reception])
        X_scaled = self.reception_scaler.transform(reception_data)
        prediction = self.service_model.predict(X_scaled)
        Y_unscaled = self.service_scaler.inverse_transform(prediction)
        return Y_unscaled