/**
 * Copyright (c) 2017 Razeware LLC
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * Notwithstanding the foregoing, you may not use, copy, modify, merge, publish,
 * distribute, sublicense, create a derivative work, and/or sell copies of the
 * Software in any work that is designed, intended, or marketed for pedagogical or
 * instructional purposes related to programming, coding, application development,
 * or information technology.  Permission for such use, copying, modification,
 * merger, publication, distribution, sublicensing, creation of derivative works,
 * or sale is expressly withheld.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

import UIKit
import CoreBluetooth
import AVFoundation


let nanoServiceCBUUID = CBUUID(string: "0xffff") //"180D"
let objectDetectionCharacteristicCBUUID = CBUUID(string: "0xbbbb") //2A37
 // let bodySensorLocationCharacteristicCBUUID = CBUUID(string: "2A38") //don't need this


class ODAViewController: UIViewController {
  

  @IBOutlet weak var detectedObjectLabel: UILabel!
  @IBOutlet weak var bodySensorLocationLabel: UILabel!

    @IBOutlet weak var swipeLabel: UILabel!
    var centralManager: CBCentralManager!
  var nanoPeripheral: CBPeripheral!
  var count = 0
  var dataReceivedFlag = false
  var audioFlag = false
  

  override func viewDidLoad() {
    super.viewDidLoad()

    centralManager = CBCentralManager(delegate: self, queue: nil)

    // Make the digits monospaces to avoid shifting when the numbers change
    detectedObjectLabel.font = UIFont.monospacedDigitSystemFont(ofSize: 30, weight: .regular)
    
    
    let leftSwipe = UISwipeGestureRecognizer(target: self, action: #selector(handleSwipes(_:)))
    let rightSwipe = UISwipeGestureRecognizer(target: self, action: #selector(handleSwipes(_:)))
        
    leftSwipe.direction = .left
    rightSwipe.direction = .right

    view.addGestureRecognizer(leftSwipe)
    view.addGestureRecognizer(rightSwipe)

  }

  @objc func handleSwipes(_ sender:UISwipeGestureRecognizer) {
          
      if (sender.direction == .left) {
          print("Swipe Left")
          audioFlag = false
      }
          
      if (sender.direction == .right) {
          print("Swipe Right")
          audioFlag = true
      }
  }
  
  func onDetectionReceived(_ detectedObject: Int) -> String {
    let dict = [0 : "Unlabeled", 1 : "Person", 2 : "Bicycle", 3 : "Car", 4 : "Motorcycle", 5 : "Airplane", 6 : "Bus", 7 : "Train", 8 : "Truck", 9 : "Boat", 10 : "Traffic Light", 11 : "Fire Hydrant", 12 : "Street Sign", 13 : "Stop Sign", 14 : "Parking Meter", 15 : "Bench", 16 : "Bird", 17 : "Cat", 18 : "Dog", 19 : "Horse", 20 : "Sheep", 21 : "Cow", 22 : "Elephant", 23 : "Bear", 24 : "Zebra", 25 : "Giraffe", 26 : "Hat", 27 : "Backpack", 28 : "Umbrella", 29 : "Shoe", 30 : "Eye Glasses", 31 : "Handbag", 32 : "Tie", 33 : "Suitcase", 34 : "Frisbee", 35 : "Skis", 36 : "Snowboard", 37 : "Sports Ball", 38 : "Kite", 39 : "Baseball Bat", 40 : "Baseball Glove", 41 : "Skateboard", 42 : "Surfboard", 43 : "Tennis Racket", 44 : "Bottle", 45 : "Plate", 46 : "Wine Glass", 47 : "Cup", 48 : "Fork", 49 : "Knife", 50 : "Spoon", 51 : "Bowl", 52 : "Banana", 53 : "Apple", 54 : "Sandwich", 55 : "Orange", 56 : "Broccoli", 57 : "Carrot", 58 : "Hot dog", 59 : "Pizza", 60 : "Donut", 61 : "Cake", 62 : "Chair", 63 : "Couch", 64 : "Potted Plant", 65 : "Bed", 66 : "Mirror", 67 : "Dining Table", 68 : "Window", 69 : "Desk", 70 : "Toilet", 71 : "Door", 72 : "TV", 73 : "Laptop", 74 : "Mouse", 75 : "Remote", 76 : "Keyboard", 77 : "Cell Phone", 78 : "Microwave", 79 : "Oven", 80 : "Toaster", 81 : "Sink", 82 : "Refrigerator", 83 : "Blender", 84 : "Book", 85 : "Clock", 86 : "Vase", 87 : "Scissors", 88 : "Teddy Bear", 89 : "Hair Drier", 90 : "Toothbrush", 95: " ", 96: " " ]
    
    detectedObjectLabel.text = dict[detectedObject]
    print("Object ID: \(String(describing: dict[detectedObject]!))")
    
    return dict[detectedObject]!
    
  }
}

extension ODAViewController: CBCentralManagerDelegate {
  func centralManagerDidUpdateState(_ central: CBCentralManager) {
    switch central.state {
    case .unknown:
      print("central.state is .unknown")
    case .resetting:
      print("central.state is .resetting")
    case .unsupported:
      print("central.state is .unsupported")
    case .unauthorized:
      print("central.state is .unauthorized")
    case .poweredOff:
      print("central.state is .poweredOff")
    case .poweredOn:
      print("central.state is .poweredOn")
      centralManager.scanForPeripherals(withServices: [nanoServiceCBUUID])
    }
  }

  func centralManager(_ central: CBCentralManager, didDiscover peripheral: CBPeripheral,
                      advertisementData: [String : Any], rssi RSSI: NSNumber) {
    print(peripheral)
    nanoPeripheral = peripheral
    nanoPeripheral.delegate = self
    centralManager.stopScan()
    centralManager.connect(nanoPeripheral)
  }

  func centralManager(_ central: CBCentralManager, didConnect peripheral: CBPeripheral) {
    print("Connected!")
    nanoPeripheral.discoverServices([nanoServiceCBUUID])
  }
  
  func centralManager(_ central: CBCentralManager, didDisconnectPeripheral peripheral: CBPeripheral, error: Error?) {
    centralManager.connect(nanoPeripheral)
  }
  
  func audio(label: String) {
    let utterance = AVSpeechUtterance(string: label)
    let synthesizer = AVSpeechSynthesizer()
    synthesizer.speak(utterance)
  }

}

//func disconnectFromDevice () {
//  if nanoPeripheral != nil {
//  centralManager?.cancelPeripheralConnection(nanoPeripheral!)
//    }
// }

extension ODAViewController: CBPeripheralDelegate {
  func peripheral(_ peripheral: CBPeripheral, didDiscoverServices error: Error?) {
    guard let services = peripheral.services else { return }
    for service in services {
      print(service)
      peripheral.discoverCharacteristics(nil, for: service)
    }
  }

  func peripheral(_ peripheral: CBPeripheral, didDiscoverCharacteristicsFor service: CBService, error: Error?) {
    guard let characteristics = service.characteristics else { return }

    for characteristic in characteristics {
      print(characteristic)

      if characteristic.properties.contains(.read) {
        print("\(characteristic.uuid): properties contains .read")
        peripheral.readValue(for: characteristic)
      }
      if characteristic.properties.contains(.notify) {
        print("\(characteristic.uuid): properties contains .notify")
        peripheral.setNotifyValue(true, for: characteristic)
      }
    }
  }

  func peripheral(_ peripheral: CBPeripheral, didUpdateValueFor characteristic: CBCharacteristic, error: Error?) {
    switch characteristic.uuid {
    case objectDetectionCharacteristicCBUUID:
        
      let objectIDList = detectedObjects(from: characteristic)
      
      if dataReceivedFlag == false {
        audio(label: "Swipe right anywhere on the screen to hear audio feedback. Swipe left anywhere to turn audio off.")
        dataReceivedFlag = true
      }
      
      print("")
      print("Length of byteArray = ", objectIDList.count)
      
      
      var objectLabels = [String : Int]()
        
        for i in objectIDList.indices {
          let object = Int(objectIDList[i])
          let label = onDetectionReceived(object)
          
          // Adds label to hashmap with value of 1 if it doesn't exist, or increments it by 1 if it does
          if objectLabels[label] != nil {
            objectLabels[label] = objectLabels[label]! + 1
          }
          else {
            objectLabels[label] = 1
          }
          
          count = count + 1
        
        //Add and check boolean flag here for whether audio is set to true or false
          if audioFlag {
            if count % 12 == 0 { //reduces audio readout
              audio(label: fixGrammar(labels: objectLabels))
            }
          }
          
      }
    default:
      print("Unhandled Characteristic UUID: \(characteristic.uuid)")
    }
  }
  
  func fixGrammar(labels: [String : Int]) -> String {
    var conjunction = ""
    var output = ""
    var ctr = 0
    for (label, number) in labels {
      if ctr > 0 {
        conjunction = " and "
      }
      if label == " " {
        return label
      }
      if number == 1 {
        output = output + " " + conjunction + String(number) + " " +  label
      }
      else {
        output = output + " " + conjunction + String(number) + " " +  pluralize(word: label)
      }
      ctr = ctr + 1
    }
    return output
  }
  
  func pluralize(word: String) -> String {
    let plural = ["Unlabeled" : "Unlabeled", "Person" : "People", "Bicycle" : "Bicycles", "Car" : "Cars", "Motorcycle" : "Motorcycles", "Airplane" : "Airplanes", "Bus" : "Buses", "Train" : "Trains", "Truck" : "Trucks", "Boat" : "Boats", "Traffic Light" : "Traffic Lights", "Fire Hydrant" : "Fire Hydrants", "Street Sign" : "Street Signs", "Stop Sign" : "Stop Signs", "Parking Meter" : "Parking Meters", "Bench" : "Benches", "Bird" : "Birds", "Cat" : "Cats", "Dog" : "Dogs", "Horse" : "Horses", "Sheep" : "Sheep", "Cow" : "Cows", "Elephant" : "Elephants", "Bear" : "Bears", "Zebra" : "Zebras", "Giraffe" : "Giraffes", "Hat" : "Hats", "Backpack" : "Backpacks", "Umbrella" : "Umbrellas", "Shoe" : "Shoes", "Eye Glasses" : "Eye Glasses", "Handbag" : "Handbags", "Tie" : "Ties", "Suitcase" : "Suitcases", "Frisbee" : "Frisbees", "Skis" : "Skis", "Snowboard" : "Snowboards", "Sports Ball" : "Sports Balls", "Kite" : "Kites", "Baseball Bat" : "Baseball Bats", "Baseball Glove" : "Baseball Gloves", "Skateboard" : "Skateboards", "Surfboard" : "Surfboards", "Tennis Racket" : "Tennis Rackets", "Bottle" : "Bottles", "Plate" : "Plates", "Wine Glass" : "Wine Glasses", "Cup" : "Cups", "Fork" : "Forks", "Knife" : "Knives", "Spoon" : "Spoons", "Bowl" : "Bowls", "Banana" : "Bananas", "Apple" : "Apples", "Sandwich" : "Sandwiches", "Orange" : "Oranges", "Broccoli" : "Broccoli", "Carrot" : "Carrots", "Hot dog" : "Hot dogs", "Pizza" : "Pizzas", "Donut" : "Donuts", "Cake" : "Cakes", "Chair" : "Chairs", "Couch" : "Couches", "Potted Plant" : "Potted Plants", "Bed" : "Beds", "Mirror" : "Mirrors", "Dining Table" : "Dining Tables", "Window" : "Windows", "Desk" : "Desks", "Toilet" : "Toilets", "Door" : "Doors", "TV" : "TVs", "Laptop" : "Laptops", "Mouse" : "Mice", "Remote" : "Remotes", "Keyboard" : "Keyboards", "Cell Phone" : "Cell Phones", "Microwave" : "Microwaves", "Oven" : "Ovens", "Toaster" : "Toasters", "Sink" : "Sinks", "Refrigerator" : "Refrigerators", "Blender" : "Blenders", "Book" : "Books", "Clock" : "Clocks", "Vase" : "Vases", "Scissors" : "Scissors", "Teddy Bear" : "Teddy Bears", "Hair Drier" : "Hair Driers", "Toothbrush" : "Toothbrushes"]
    
    return plural[word]!
  }

  //Returns list of objects detected in a given image instance
  private func detectedObjects(from characteristic: CBCharacteristic) -> Array<UInt8> {
    guard let characteristicData = characteristic.value else { return [UInt8](arrayLiteral: 97) }
    let detectedIDs = [UInt8](characteristicData)
    return detectedIDs
  }
}


