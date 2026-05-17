import { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert } from 'react-native';
import * as LocalAuthentication from 'expo-local-authentication';

export function LoginScreen({ navigation }: any) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const login = async () => {
    // TODO: API call
    Alert.alert('Login', `${username} kirishga harakat qilmoqda...`);
  };

  const biometricLogin = async () => {
    const hasHardware = await LocalAuthentication.hasHardwareAsync();
    if (!hasHardware) return Alert.alert('Biometric mavjud emas');
    const result = await LocalAuthentication.authenticateAsync({
      promptMessage: 'UniAnalytics ga kirish',
    });
    if (result.success) {
      Alert.alert('Kirildi!');
      navigation.navigate('Dashboard');
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>🎓 UniAnalytics</Text>
      <TextInput style={styles.input} placeholder="Username" value={username} onChangeText={setUsername} />
      <TextInput style={styles.input} placeholder="Parol" value={password} onChangeText={setPassword} secureTextEntry />
      <TouchableOpacity style={styles.button} onPress={login}>
        <Text style={styles.btnText}>Kirish</Text>
      </TouchableOpacity>
      <TouchableOpacity style={[styles.button, { backgroundColor: '#10b981' }]} onPress={biometricLogin}>
        <Text style={styles.btnText}>🔐 Face ID / Touch ID</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 24, justifyContent: 'center', backgroundColor: '#fff' },
  title: { fontSize: 32, fontWeight: 'bold', textAlign: 'center', marginBottom: 32, color: '#1677ff' },
  input: { borderWidth: 1, borderColor: '#ddd', borderRadius: 8, padding: 12, marginBottom: 12 },
  button: { backgroundColor: '#1677ff', padding: 14, borderRadius: 8, marginTop: 8 },
  btnText: { color: 'white', textAlign: 'center', fontWeight: '600' },
});
