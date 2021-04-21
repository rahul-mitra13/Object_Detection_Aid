# Object Detection Aid

## Hardware Dependencies

1. [NVIDIA Jetson Nano Developer Kit](https://developer.nvidia.com/embedded/jetson-nano-developer-kit)
2. [Raspberry Pi V2 Camera](https://www.raspberrypi.org/products/camera-module-v2/)
3. Portable Battery ([This is the one we used](https://www.amazon.com/INIU-Portable-20000mAh-High-speed-Flashlight/dp/B07YPY31FL))
4. [Bluetooth module for the Nano](https://www.amazon.com/Makeronics-Wireless-Bluetooth-Assembly-Instruction/dp/B07X2NLL85/ref=sr_1_2_sspa?dchild=1&keywords=intel+8265ngw&qid=1618940446&sr=8-2-spons&psc=1&spLa=ZW5jcnlwdGVkUXVhbGlmaWVyPUFQS0syQ1NSMFJGRjImZW5jcnlwdGVkSWQ9QTAzMzMxMTEyU0VFSjc4VDlPM09GJmVuY3J5cHRlZEFkSWQ9QTA3ODI0NzIxUEM2TUo0NE1GNU01JndpZGdldE5hbWU9c3BfYXRmJmFjdGlvbj1jbGlja1JlZGlyZWN0JmRvTm90TG9nQ2xpY2s9dHJ1ZQ==)

## ODA: How it works

This is an object detection aid for the visually imparied that consists of a white cane enhanced with a microcomputer and camera and an iOS application. As you use this white cane throughout your daily routine, you can use its object detection capabilities to receive helpful information about your environment! Specifically, the cane’s camera and microcomputer detect objects in front of you via machine learning, and then send that information via Bluetooth to your smartphone, where it can be relayed to you via audio feedback.


## Software Dependencies

1. [iOS Swift](https://developer.apple.com/swift/)
2. [XCode](https://developer.apple.com/xcode/)
3. [Tensor Flow Object Detection API](https://www.tensorflow.org/api_docs)

   The network we're using is ssd-inception-v2 which has 91 object classes

3. [BlueZ](http://www.bluez.org/)
4. [DBus](https://www.freedesktop.org/wiki/Software/dbus/)

## Usage 

### Manual Compilation 

#### Jetson Nano 

Once the Jetson Nano has been set up, open the terminal and clone this repo. 

`git clone https://github.com/rahul-mitra13/Object_Detection_Aid`

Change directory to the gatt-server directory.

`cd /Senior_Project/gatt-server`

Run gatt-server.py. 

`python gatt-server.py`

#### iOS Smartphone

Clone this repo as above. Under the `ObjectDetectionAid` directory, open `ObjectDetectionAid.xcodeproj` with XCode. Turn smartphone's bluetooth on and build this project. 

### Compilation on Startup

#### Jetson Nano 

Once the jetson nano is set up, open `.bashrc`.

`vim .bashrc` 

Add the following line at the end of the `.bashrc`. 

`python ~/Object_Detection_Aid/gatt-server/gatt-server.py`

Add `gnome-terminal` to Nano's startup applications. 

#### iOS Smartphone 

Same as the case for manual compilation.






