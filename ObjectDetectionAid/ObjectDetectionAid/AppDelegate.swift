import UIKit
import AVFoundation

@UIApplicationMain
class AppDelegate: UIResponder, UIApplicationDelegate {

  var window: UIWindow?

  func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplicationLaunchOptionsKey: Any]?) -> Bool {
    return true
  }
  
  
  // Makes sure that audio does not stop in the background
  func applicationDidEnterBackground(_ application: UIApplication) {
    
    let utterance = AVSpeechUtterance(string: "  ")
    let synthesizer = AVSpeechSynthesizer()
    synthesizer.speak(utterance)
    
    do{
      let _ = try AVAudioSession.sharedInstance().setCategory(AVAudioSessionCategoryPlayback,
                                                                   with: .duckOthers)
      } catch{
          print(error)
      }
  }
  
  func applicationDidBecomeActive(_ application: UIApplication) {
    // AVSpeechSynthesizer will be automatically resumed
    print("applicationDidBecomeActive")
  }
  
}
