//
//  ViewController.swift
//  home-alert-controller
//
//  Created by Naookie Sato on 3/6/19.
//  Copyright © 2019 Naookie Sato. All rights reserved.
//

import UIKit

class ViewController: UIViewController {

    static var serverUrl = "http://10.0.0.138/"
    // TODO: Remove this and make location a selection, querying the main server
    static var location = "front_door"

    /**
     * This returns a tuple, response code and the page response data.
     * -1 status code indicates error.
     */
    func makeRequest(url: String) -> (statusCode: Int, responseString: String) {
      var responseString = ""
      var statusCode = -1
      let session = URLSession.shared
      let semaphore = DispatchSemaphore(value: 0)
      let task = session.dataTask(with: URL(string: url)!) { data, response, error in
        guard error == nil else {
          // TODO: Handle errors better
          print(error!)
          semaphore.signal()
          return
        }
        statusCode = (response as! HTTPURLResponse).statusCode
        guard let data = data else {
          semaphore.signal()
          return
        }
        responseString = String(data: data, encoding: .utf8)!
        semaphore.signal()
      }
      task.resume()
      semaphore.wait()
      return (statusCode: statusCode, responseString: responseString)
    }

    @IBAction func lockButton(sender: UIButton) {
      let lockUrl = ViewController.serverUrl + ViewController.location + "/arm"
      let response = makeRequest(url: lockUrl)
      var alertTitle = "Email notifications on"
      var alertMessage = response.responseString
      if response.statusCode != 200 {
        alertTitle = "Error: " + String(response.statusCode)
        alertMessage = "Did not successfully make request to server."
      }
      let alertController = UIAlertController(title: alertTitle, message: alertMessage,
        preferredStyle: UIAlertController.Style.alert)
      alertController.addAction(UIAlertAction(title: "OK", style: UIAlertAction.Style.default, handler: nil))
      present(alertController, animated: true, completion: nil)
    }

    @IBAction func unlockButton(sender: UIButton) {
      let unlockUrl = ViewController.serverUrl + ViewController.location + "/disarm"
      let response = makeRequest(url: unlockUrl)
      var alertTitle = "Email notifications off"
      var alertMessage = response.responseString
      if response.statusCode != 200 {
        alertTitle = "Error: " + String(response.statusCode)
        alertMessage = "Did not successfully make request to server."
      }
      let alertController = UIAlertController(title: alertTitle, message: alertMessage,
        preferredStyle: UIAlertController.Style.alert)
      alertController.addAction(UIAlertAction(title: "OK", style: UIAlertAction.Style.default, handler: nil))
      present(alertController, animated: true, completion: nil)
    }

    @IBAction func statusButton(sender: UIButton) {
      let statusUrl = ViewController.serverUrl + ViewController.location
      let response = makeRequest(url: statusUrl)
      var alertTitle = "Front door status:"
      var alertMessage = response.responseString
      if response.statusCode != 200 {
        alertTitle = "Error: " + String(response.statusCode)
        alertMessage = "Did not successfully make request to server."
      }
      let alertController = UIAlertController(title: alertTitle, message: alertMessage,
        preferredStyle: UIAlertController.Style.alert)
      alertController.addAction(UIAlertAction(title: "OK", style: UIAlertAction.Style.default, handler: nil))
      present(alertController, animated: true, completion: nil)
    }

    @IBAction func triggerButton(sender: UIButton) {
      let triggerUrl = ViewController.serverUrl + ViewController.location + "/trigger"
      let response = makeRequest(url: triggerUrl)
      var alertTitle = "Front door manual trigger:"
      var alertMessage = response.responseString
      if response.statusCode != 200 {
        alertTitle = "Error: " + String(response.statusCode)
        alertMessage = "Did not successfully make request to server."
      }
      let alertController = UIAlertController(title: alertTitle, message: alertMessage,
        preferredStyle: UIAlertController.Style.alert)
      alertController.addAction(UIAlertAction(title: "OK", style: UIAlertAction.Style.default, handler: nil))
      present(alertController, animated: true, completion: nil)
    }

    override func viewDidLoad() {
        super.viewDidLoad()
        // Do any additional setup after loading the view, typically from a nib.
    }

}

