import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Alert } from 'react-native';
import * as Camera from 'expo-camera';

const schedule = [
  { day: 'Dushanba', time: '9:00', subject: 'Matematik analiz', room: 'A-301' },
  { day: 'Dushanba', time: '11:00', subject: 'Fizika', room: 'B-205' },
  { day: 'Seshanba', time: '9:00', subject: 'Algoritmlar', room: 'C-102' },
];

export function ScheduleScreen() {
  const scanQR = async () => {
    const { status } = await Camera.Camera.requestCameraPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Kamera ruxsati kerak');
      return;
    }
    Alert.alert('QR scan', 'Davomatni belgilash uchun QR kodni skanerlang');
  };

  return (
    <ScrollView style={styles.container}>
      <TouchableOpacity style={styles.scanBtn} onPress={scanQR}>
        <Text style={styles.scanText}>📷 QR scan — davomatni belgilash</Text>
      </TouchableOpacity>

      {schedule.map((s, i) => (
        <View key={i} style={styles.item}>
          <Text style={styles.day}>{s.day}</Text>
          <Text style={styles.subject}>{s.subject}</Text>
          <View style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
            <Text style={styles.meta}>🕐 {s.time}</Text>
            <Text style={styles.meta}>🚪 {s.room}</Text>
          </View>
        </View>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f7fa' },
  scanBtn: { margin: 12, padding: 16, backgroundColor: '#1677ff', borderRadius: 12 },
  scanText: { color: 'white', textAlign: 'center', fontSize: 16, fontWeight: '600' },
  item: { margin: 8, padding: 16, backgroundColor: 'white', borderRadius: 12 },
  day: { fontSize: 12, color: '#666' },
  subject: { fontSize: 16, fontWeight: '600', marginVertical: 4 },
  meta: { color: '#1677ff' },
});
