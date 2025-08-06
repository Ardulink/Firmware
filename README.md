# 📡 Ardulink-2 Firmware

Welcome to the official repository for the **Ardulink-2 Firmware** — an open-source Arduino firmware implementing the **Ardulink Protocol** for seamless communication with Java applications via **Serial, MQTT, TCP/IP, Bluetooth**, and more.

This repo hosts:
- 📄 **Source code** for the firmware
- 📖 **Documentation for the protocol**
- 📦 **Pre-compiled HEX files** ready for uploading to Arduino boards via our [GitHub Releases](#-releases)
- 📝 **Examples** demonstrating how to add custom code and extend the firmware in the [`examples/`](./examples) subdirectory  

---

## 📦 Releases

Ready-to-use precompiled `.hex` files for various Arduino boards (e.g. Uno, Nano, Mega) are available on the [Releases Page](https://github.com/Ardulink/Firmware/releases).  

You can upload these using tools like:
- [XLoader](http://russemotto.com/xloader/) (Windows)
- [avrdude](https://github.com/avrdudes/avrdude) (macOS/Linux/Windows)
- [Arduino IDE](https://www.arduino.cc/en/software/) (for flashing manually built sketches)

---

## 📖 Protocol Documentation

Detailed documentation for the **Ardulink Protocol** — including command structure, parameters, response types, and subscription mechanisms — can be found in the [📖 Ardulink2 Specification](./Ardulink2-Specification.md).

---

## 🛠️ Build Instructions

If you prefer to build the firmware from source:

1. Install the [Arduino IDE](https://www.arduino.cc/en/software)
2. Open the `ArdulinkProtocol/ArdulinkProtocol.ino` sketch
3. Select your target board and port
4. Click **Upload**

---

## 📣 Contributions

Contributions, feature requests, and protocol extensions are welcome!  
Feel free to open an [Issue](https://github.com/Ardulink/Firmware/issues) or submit a [Pull Request](https://github.com/Ardulink/Firmware/pulls).

---

## 🔗 Related Projects

- [Ardulink-2 Java Library](https://github.com/Ardulink/Ardulink-2) — Java framework for communicating with Arduino devices using different transports.

