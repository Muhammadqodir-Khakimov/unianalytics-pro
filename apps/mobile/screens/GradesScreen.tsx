import { View, Text, FlatList, StyleSheet } from 'react-native';

const grades = [
  { subject: 'Matematik analiz', grade: 85, color: '#10b981' },
  { subject: 'Algoritmlar', grade: 72, color: '#3b82f6' },
  { subject: 'Fizika', grade: 68, color: '#f59e0b' },
  { subject: 'Iqtisodiyot', grade: 91, color: '#10b981' },
];

export function GradesScreen() {
  return (
    <View style={styles.container}>
      <FlatList
        data={grades}
        keyExtractor={(item, i) => String(i)}
        renderItem={({ item }) => (
          <View style={styles.item}>
            <Text style={styles.subject}>{item.subject}</Text>
            <View style={[styles.badge, { backgroundColor: item.color }]}>
              <Text style={styles.grade}>{item.grade}</Text>
            </View>
          </View>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f7fa' },
  item: { backgroundColor: 'white', margin: 8, padding: 16, borderRadius: 12, flexDirection: 'row', justifyContent: 'space-between' },
  subject: { fontSize: 16, fontWeight: '500' },
  badge: { paddingHorizontal: 12, paddingVertical: 4, borderRadius: 6 },
  grade: { color: 'white', fontWeight: 'bold' },
});
