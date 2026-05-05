import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import PoseStamped # Gazebo'dan gelen konum mesaj tipi (gerekirse Point veya Odometry ile değiştir)
# from geometry_msgs.msg import Twist  # GELECEKTE: Robotu hareket ettirmek için eklenecek
import json
import csv
import os
from datetime import datetime

class MainControllerNode(Node):
    def __init__(self):
        super().__init__('main_controller_node')
        
        # --- 1. SENSÖR VE VERİ DİNLEME (SUBSCRIBERS) ---
        # Simülasyondan (veya ileride gerçek RTK GPS/Odometry'den) gelen konum
        self.loc_sub = self.create_subscription(PoseStamped, 'real_location', self.location_callback, 10)
        
        # Yapay Zeka (Vision) Modülünden gelen hastalık tespitleri
        self.ai_sub = self.create_subscription(String, 'ai/detections', self.ai_callback, 10)
        
        # --- 2. HAREKET VE KONTROL (PUBLISHERS) ---
        # GELECEKTE: Otonom sürüş veya robot kol kontrolü için publisher'lar buraya eklenecek
        # self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        
        # --- DURUM DEĞİŞKENLERİ ---
        self.latest_location = None
        self.location_ready = False
        
        # --- VERİ KAYIT (LOGLAMA) ALTYAPISI ---
        self.csv_file_path = os.path.join(os.path.expanduser('~'), 'Desktop', 'robotanik_analiz_raporu.csv')
        self.init_csv_file()
        
        self.get_logger().info('Main Controller (Sistem Beyni) başlatıldı. Sensör verileri bekleniyor...')

    def init_csv_file(self):
        file_exists = os.path.isfile(self.csv_file_path)
        with open(self.csv_file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(['Zaman', 'Hastalik_Turu', 'Risk_Skoru(%)', 'Yayilma_Orani(%)', 'Konum_X', 'Konum_Y'])

    def location_callback(self, msg):
        # Konum verisi sürekli güncellenir (Simülasyon veya Gerçek Sensör)
        self.latest_location = msg
        if not self.location_ready:
            self.location_ready = True
            self.get_logger().info('Konum verisi kilitlendi! Sistem tam otonomi/loglama için hazır.')

    def ai_callback(self, msg):
        # GÜVENLİK DUVARI: Konum bilgisi yoksa, veriyi işleme
        if not self.location_ready or self.latest_location is None:
            return

        try:
            data = json.loads(msg.data)
            label = data.get('label', 'Bilinmiyor')
            risk = data.get('risk_score', 0.0)
            spread = data.get('spread_ratio', 0.0)
            
            # Anlık konumu çek
            x = self.latest_location.pose.position.x
            y = self.latest_location.pose.position.y
            
            # Gerçek zamanı al
            current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # CSV'ye Kaydet
            with open(self.csv_file_path, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([current_time_str, label, f"{risk:.1f}", f"{spread:.1f}", f"{x:.3f}", f"{y:.3f}"])
                
            self.get_logger().info(f"[LOGLANDI] Hedef: {label} | Risk: %{risk:.1f} | Konum: (X:{x:.2f}, Y:{y:.2f})")
            
            # GELECEKTE: Burada 'Eğer risk %70'ten büyükse robotu durdur (cmd_vel) ve ilaç sık' gibi komutlar olacak.

        except json.JSONDecodeError:
            self.get_logger().error('AI verisi JSON formatında çözülemedi!')

def main(args=None):
    rclpy.init(args=args)
    node = MainControllerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()