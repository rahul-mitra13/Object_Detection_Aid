from __future__ import print_function
import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service
import array
import functools
import time

try:
  from gi.repository import GObject
except ImportError:
  import gobject as GObject

from random import randint

import exceptions
import adapters

BLUEZ_SERVICE_NAME = 'org.bluez'
LE_ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'
DBUS_OM_IFACE = 'org.freedesktop.DBus.ObjectManager'
DBUS_PROP_IFACE = 'org.freedesktop.DBus.Properties'

LE_ADVERTISEMENT_IFACE = 'org.bluez.LEAdvertisement1'

GATT_MANAGER_IFACE = 'org.bluez.GattManager1'

GATT_SERVICE_IFACE = 'org.bluez.GattService1'
GATT_CHRC_IFACE =    'org.bluez.GattCharacteristic1'
GATT_DESC_IFACE =    'org.bluez.GattDescriptor1'






import jetson.inference
import jetson.utils
import sys

# Temporarily global 
ids = []
num_ids = 0

# Returns a list of the ClassIDs of the identified objects (0 - 90)
def detected_ids(detections):
	for i in range(len(detections)):
		ids.append(detections[i].ClassID)
	num_ids = len(detections)

# Gets current list of ClassIDs of identified objects(0 - 90)
def get_ids():
	return ids

def reset_ids():
	del ids[:]


class Application(dbus.service.Object):
    """
    org.bluez.GattApplication1 interface implementation
    """
    # Creates an application
    def __init__(self, bus):
        self.path = '/'
        self.services = []
        dbus.service.Object.__init__(self, bus, self.path)

	# Adding all services to our peripheral application 
        self.add_service(HeartRateService(bus, 0))
        
	"""
        self.add_service(BatteryService(bus, 1))
        self.add_service(TestService(bus, 2))

        """

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_service(self, service):
        self.services.append(service)
    
    def get_service(self):
	return self.services[0]

    @dbus.service.method(DBUS_OM_IFACE, out_signature='a{oa{sa{sv}}}')
    def GetManagedObjects(self):
        response = {}
        print('GetManagedObjects')

	# Every service has characteristics that in turn have descriptors
        for service in self.services:
            response[service.get_path()] = service.get_properties()
            chrcs = service.get_characteristics()
            for chrc in chrcs:
                response[chrc.get_path()] = chrc.get_properties()
                descs = chrc.get_descriptors()
                for desc in descs:
                    response[desc.get_path()] = desc.get_properties()

        return response


class Service(dbus.service.Object):
    """
    org.bluez.GattService1 interface implementation
    """
    PATH_BASE = '/org/bluez/example/service'

    # Creates a service
    def __init__(self, bus, index, uuid, primary):
        self.path = self.PATH_BASE + str(index)
        self.bus = bus
        self.uuid = uuid
        self.primary = primary
        self.characteristics = []
        dbus.service.Object.__init__(self, bus, self.path)

    # Gets the properties of a service: UUID, primary, and its characteristics
    def get_properties(self):
        return {
                GATT_SERVICE_IFACE: {
                        'UUID': self.uuid,
                        'Primary': self.primary,
                        'Characteristics': dbus.Array(
                                self.get_characteristic_paths(),
                                signature='o')
                }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    # Adds a characteristic to a service 
    def add_characteristic(self, characteristic):
        self.characteristics.append(characteristic)

    def get_characteristic_paths(self):
        result = []
        for chrc in self.characteristics:
            result.append(chrc.get_path())
        return result

    # Gets a service's characteristics 
    def get_characteristics(self):
        return self.characteristics

    # Gets the properties of all of the services of an application 
    @dbus.service.method(DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != GATT_SERVICE_IFACE:
            raise exceptions.InvalidArgsException()

        return self.get_properties()[GATT_SERVICE_IFACE]


class Characteristic(dbus.service.Object):
    """
    org.bluez.GattCharacteristic1 interface implementation
    """
    # Creates a characteristic 
    def __init__(self, bus, index, uuid, flags, service):
        self.path = service.path + '/char' + str(index)
        self.bus = bus
        self.uuid = uuid
        self.service = service
        self.flags = flags
        self.descriptors = []
        dbus.service.Object.__init__(self, bus, self.path)

    # Gets properties of a characteristic: service, UUID, flags and descriptors
    def get_properties(self):
        return {
                GATT_CHRC_IFACE: {
                        'Service': self.service.get_path(),
                        'UUID': self.uuid,
                        'Flags': self.flags,
                        'Descriptors': dbus.Array(
                                self.get_descriptor_paths(),
                                signature='o')
                }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    # Adds descriptors to a characteristic 
    def add_descriptor(self, descriptor):
        self.descriptors.append(descriptor)

    def get_descriptor_paths(self):
        result = []
        for desc in self.descriptors:
            result.append(desc.get_path())
        return result
    
    # Gets a characteristic's descriptors 
    def get_descriptors(self):
        return self.descriptors

    # Gets the properties of all of the characteristics of a service  
    @dbus.service.method(DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != GATT_CHRC_IFACE:
            raise exceptions.InvalidArgsException()

        return self.get_properties()[GATT_CHRC_IFACE]

    # Error Handling in the case that this function is called for an undefined characteristic 
    @dbus.service.method(GATT_CHRC_IFACE,
                        in_signature='a{sv}',
                        out_signature='ay')
    def ReadValue(self, options):
        print('Default ReadValue called, returning error')
        raise exceptions.NotSupportedException()

    @dbus.service.method(GATT_CHRC_IFACE, in_signature='aya{sv}')
    def WriteValue(self, value, options):
        print('Default WriteValue called, returning error')
        raise exceptions.NotSupportedException()

    @dbus.service.method(GATT_CHRC_IFACE)
    def StartNotify(self):
        print('Default StartNotify called, returning error')
        raise exceptions.NotSupportedException()

    @dbus.service.method(GATT_CHRC_IFACE)
    def StopNotify(self):
        print('Default StopNotify called, returning error')
        raise exceptions.NotSupportedException()

    @dbus.service.signal(DBUS_PROP_IFACE,
                         signature='sa{sv}as')
    def PropertiesChanged(self, interface, changed, invalidated):
        pass


class Descriptor(dbus.service.Object):
    """
    org.bluez.GattDescriptor1 interface implementation
    """
    # Creates a descriptor
    def __init__(self, bus, index, uuid, flags, characteristic):
        self.path = characteristic.path + '/desc' + str(index)
        self.bus = bus
        self.uuid = uuid
        self.flags = flags
        self.chrc = characteristic
        dbus.service.Object.__init__(self, bus, self.path)

    # Gets the properties of a descriptor
    def get_properties(self):
        return {
                GATT_DESC_IFACE: {
                        'Characteristic': self.chrc.get_path(),
                        'UUID': self.uuid,
                        'Flags': self.flags,
                }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    # Gets all of the descriptors of a characteristic 
    @dbus.service.method(DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != GATT_DESC_IFACE:
            raise exceptions.InvalidArgsException()

        return self.get_properties()[GATT_DESC_IFACE]

    # Error Handling in the case that this function is called for an undefined descriptor 
    @dbus.service.method(GATT_DESC_IFACE,
                        in_signature='a{sv}',
                        out_signature='ay')
    def ReadValue(self, options):
        print('Default ReadValue called, returning error')
        raise exceptions.NotSupportedException()

    @dbus.service.method(GATT_DESC_IFACE, in_signature='aya{sv}')
    def WriteValue(self, value, options):
        print('Default WriteValue called, returning error')
        raise exceptions.NotSupportedException()


class HeartRateService(Service):
    """
    Fake Heart Rate Service that simulates a fake heart beat and control point
    behavior.

    """
    # Service UUID
    HR_UUID = '0000ffff-0000-1000-8000-00805f9b34fb'

    # Creates the Heart Rate Service, adding its characteristics 
    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.HR_UUID, True)
        self.add_characteristic(HeartRateMeasurementChrc(bus, 0, self))
	self.energy_expended = 0
	"""
        self.add_characteristic(BodySensorLocationChrc(bus, 1, self))
        self.add_characteristic(HeartRateControlPointChrc(bus, 2, self))
	"""
    


class HeartRateMeasurementChrc(Characteristic):
    # Characteristic UUID
    HR_MSRMT_UUID = '0000bbbb-0000-1000-8000-00805f9b34fb'

    # Creates a characteristic that notifies the central application, but with notify set to false 
    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.HR_MSRMT_UUID,
                ['notify'],
                service)
        self.notifying = False # usually false
        self.hr_ee_count = 0 # energy expended

    # Changing heart rate measurement value
    def hr_msrmt_cb(self):
	print("In hr_msrmt_cb()")
        value = []
	detections = get_ids()
	print("Detected objects: ", detections)


	if len(detections) != 0:
		for obj in range(0, len(detections)):
        		value.append(dbus.Byte(detections[obj]))
			self.PropertiesChanged(GATT_CHRC_IFACE, { 'Value': value }, [])
			del value[:]
	else:
		value.append(dbus.Byte(95))
		self.PropertiesChanged(GATT_CHRC_IFACE, { 'Value': value }, [])

	
        	# Changing heart rate measurement to be sent via Bluetooth
        	#value.append(dbus.Byte(5))
	

	"""
        if self.hr_ee_count % 10 == 0:
            value[0] = dbus.Byte(value[0] | 0x08)
            value.append(dbus.Byte(self.service.energy_expended & 0xff))
            value.append(dbus.Byte((self.service.energy_expended >> 8) & 0xff))

        self.service.energy_expended = \
                min(0xffff, self.service.energy_expended + 1)
        self.hr_ee_count += 1

	"""
      	
	"""
        if len(returnList) != 0:
		# 0 should be an index that is iterated through over time 
		print('Updating value: ' + repr(returnList[0])) 

		 # Changes heart rate measurement value  
		self.PropertiesChanged(GATT_CHRC_IFACE, { 'Value': returnList[0] }, [])
	else:
		print("print")
		self.PropertiesChanged(GATT_CHRC_IFACE, { 'Value': 5 }, [])
		
	
        return self.notifying # true or false value
	
	"""
	
	#print('Updating value: ' + repr(value))



        #return self.notifying


    # Updates the characteristic's heart rate measurement value if notify is set to true
    def _update_hr_msrmt_simulation(self):
        print("In _update_hr_msrmt_simulation()")

        if not self.notifying:
	    #print("not notifying")
            return False
	else:
	    return True
	
        # Waits 1000 milliseconds before updating the value again 
        #GObject.timeout_add(1000, self.hr_msrmt_cb)
	

    # Sets notify to true and starts the periodic updating of the heart rate measurement
    def StartNotify(self):
	print("In StartNotify()")
        if self.notifying:
            print('Already notifying, nothing to do')
            return

        self.notifying = True
        self.StartObjectDetection()

    # Sets notify to false so that the periodic updating of the heart rate measurement stops
    def StopNotify(self):
	print("In StopNotify()")
        if not self.notifying:
            print('Not notifying, nothing to do')
            return

        self.notifying = False
        self._update_hr_msrmt_simulation()


    def StartObjectDetection(self):
	print("In StartObjectDetection()")
	#this is the neural net
	#0.5 baseline
	net = jetson.inference.detectNet("ssd-inception-v2", threshold=0.5)#threshold influences number of objects detected

	#this is the camera object
	#parameters - width, height, device file
	#a good resolution might be 1280*780
	camera = jetson.utils.videoSource("csi://0")

	# Open display to show results  
	display = jetson.utils.videoOutput("display://0")

	# Returns true if display window is still open
	while display.IsStreaming():
		reset_ids()
			
		#return img - blocks until next frame is available
		#converts raw format of the camera to floating point RGBA on the GPU
		img = camera.Capture()
		
		#Resizing image
		#imgOutput = jetson.utils.cudaAllocMapped(width=img.width*0.5, height=img.height*0.5, format=img.format)
		#jetson.utils.cudaResize(img, imgOutput)
			
		#detectNet object to identify objects
		detections = net.Detect(img)
			
		detected_ids(detections)

		# Gets HeartRateMeasurementChrc and calls the update function on it
		#app.get_service().get_characteristics()[0]._update_hr_msrmt_simulation()
		self.hr_msrmt_cb()

		#render overlayed img to the OpenGL window
		display.Render(img)
			
		#update title of window to reflect current performance - uses internal profiling mechanism
		#display.SetStatus("Object Detection | Network {:.0f} FPS".format(net.GetNetworkFPS()))
	


"""
class HeartRateService(Service):
    
    Fake Heart Rate Service that simulates a fake heart beat and control point behavior.

   
    # Service UUID
    HR_UUID = '0000180d-0000-1000-8000-00805f9b34fb'

    # Creates the Heart Rate Service, adding its characteristics 
    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.HR_UUID, True)
        self.add_characteristic(HeartRateMeasurementChrc(bus, 0, self))
        self.add_characteristic(BodySensorLocationChrc(bus, 1, self))
        self.add_characteristic(HeartRateControlPointChrc(bus, 2, self))
        self.energy_expended = 0


class HeartRateMeasurementChrc(Characteristic):
    # Characteristic UUID
    HR_MSRMT_UUID = '00002a37-0000-1000-8000-00805f9b34fb'

    # Creates a characteristic that notifies the central application, but with notify set to false 
    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.HR_MSRMT_UUID,
                ['notify'],
                service)
        self.notifying = False
        self.hr_ee_count = 0 # energy expended

    # Changing heart rate measurement value
    def hr_msrmt_cb(self):
        value = []
        value.append(dbus.Byte(0x06))
	
        # Changing heart rate measurement to be sent via Bluetooth
        value.append(dbus.Byte(randint(90, 130)))

        if self.hr_ee_count % 10 == 0:
            value[0] = dbus.Byte(value[0] | 0x08)
            value.append(dbus.Byte(self.service.energy_expended & 0xff))
            value.append(dbus.Byte((self.service.energy_expended >> 8) & 0xff))

        self.service.energy_expended = \
                min(0xffff, self.service.energy_expended + 1)
        self.hr_ee_count += 1


        print('Updating value: ' + repr(value)) # prints the object

        # Changes heart rate measurement value  
        self.PropertiesChanged(GATT_CHRC_IFACE, { 'Value': value }, [])

        return self.notifying # true or false value


    # Updates the characteristic's heart rate measurement value if notify is set to true
    def _update_hr_msrmt_simulation(self):
        print('Update HR Measurement Simulation')

        if not self.notifying:
            return
	
        # Waits 1000 milliseconds before updating the value again 
        GObject.timeout_add(1000, self.hr_msrmt_cb)

    # Sets notify to true and starts the periodic updating of the heart rate measurement
    def StartNotify(self):
        if self.notifying:
            print('Already notifying, nothing to do')
            return

        self.notifying = True
        self._update_hr_msrmt_simulation()

    # Sets notify to false so that the periodic updating of the heart rate measurement stops
    def StopNotify(self):
        if not self.notifying:
            print('Not notifying, nothing to do')
            return

        self.notifying = False
        self._update_hr_msrmt_simulation()


class BodySensorLocationChrc(Characteristic):
    # Characteristic UUID
    BODY_SNSR_LOC_UUID = '00002a38-0000-1000-8000-00805f9b34fb'

    # Creates a read only characteristic with a constant value
    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.BODY_SNSR_LOC_UUID,
                ['read'],
                service)

    def ReadValue(self, options):
        # Return 'Chest' as the sensor location.
        return [ 0x01 ]

class HeartRateControlPointChrc(Characteristic):
    # Characteristic UUID
    HR_CTRL_PT_UUID = '00002a39-0000-1000-8000-00805f9b34fb'

    # Creates a write only characteristic
    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.HR_CTRL_PT_UUID,
                ['write'],
                service)

    # Resets service's enery expended value to 0 if the central sends 1
    def WriteValue(self, value, options):
        print('Heart Rate Control Point WriteValue called')

        if len(value) != 1:
            raise exceptions.InvalidValueLengthException()

        byte = value[0]
        print('Control Point value: ' + repr(byte))

        if byte != 1:
            raise exceptions.FailedException("0x80")

        print('Energy Expended field reset!')
        self.service.energy_expended = 0


class BatteryService(Service):
    
    Fake Battery service that emulates a draining battery.

    
    # Service UUID
    BATTERY_UUID = '180f'

    # Creates a battery service 
    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.BATTERY_UUID, True)
        self.add_characteristic(BatteryLevelCharacteristic(bus, 0, self))


class BatteryLevelCharacteristic(Characteristic):
    
    Fake Battery Level characteristic. The battery level is drained by 2 points
    every 5 seconds.

    # Characteristic UUID
    BATTERY_LVL_UUID = '2a19'

    # Creates a characteristic that reads and notifies, but with notify set to false 
    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.BATTERY_LVL_UUID,
                ['read', 'notify'],
                service)
        self.notifying = False
        self.battery_lvl = 100 # initial battery level 
        GObject.timeout_add(5000, self.drain_battery) # drains the battery every 5000 milliseconds

    # Changes the battery level if notify is set to true
    def notify_battery_level(self):
        if not self.notifying:
            return
        self.PropertiesChanged(
                GATT_CHRC_IFACE,
                {'Value': [dbus.Byte(self.battery_lvl)] }, [])

    # Changes the battery level
    def drain_battery(self):
        if self.battery_lvl > 0:
            self.battery_lvl -= 2
            if self.battery_lvl < 0:
                self.battery_lvl = 0
        print('Battery level: ' + repr(self.battery_lvl))
        self.notify_battery_level()
        return True

    # Reads the current battery level 
    def ReadValue(self, options):
        print('Battery level read: ' + repr(self.battery_lvl))
        return [dbus.Byte(self.battery_lvl)]
    
    # Sets notify to true and starts the periodic updating of the battery level
    def StartNotify(self):
        if self.notifying:
            print('Already notifying, nothing to do')
            return

        self.notifying = True
        self.notify_battery_level()

    # Sets notify to false so that the periodic updating of the battery level stops
    def StopNotify(self):
        if not self.notifying:
            print('Not notifying, nothing to do')
            return

        self.notifying = False


class TestService(Service):
   
    Dummy test service that provides characteristics and descriptors that exercise various API functionality.

    TEST_SVC_UUID = '12345678-1234-5678-1234-56789abcdef0'

    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.TEST_SVC_UUID, True)
        self.add_characteristic(TestCharacteristic(bus, 0, self))
        self.add_characteristic(TestEncryptCharacteristic(bus, 1, self))
        self.add_characteristic(TestSecureCharacteristic(bus, 2, self))

class TestCharacteristic(Characteristic):
   
    Dummy test characteristic. Allows writing arbitrary bytes to its value, and
    contains "extended properties", as well as a test descriptor.

   
    TEST_CHRC_UUID = '12345678-1234-5678-1234-56789abcdef1'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.TEST_CHRC_UUID,
                ['read', 'write', 'writable-auxiliaries'],
                service)
        self.value = []
        self.add_descriptor(TestDescriptor(bus, 0, self))
        self.add_descriptor(
                CharacteristicUserDescriptionDescriptor(bus, 1, self))

    def ReadValue(self, options):
        print('TestCharacteristic Read: ' + repr(self.value))
        return self.value

    def WriteValue(self, value, options):
        print('TestCharacteristic Write: ' + repr(value))
        self.value = value


class TestDescriptor(Descriptor):
    
    Dummy test descriptor. Returns a static value.

   
    TEST_DESC_UUID = '12345678-1234-5678-1234-56789abcdef2'

    def __init__(self, bus, index, characteristic):
        Descriptor.__init__(
                self, bus, index,
                self.TEST_DESC_UUID,
                ['read', 'write'],
                characteristic)

    def ReadValue(self, options):
        return [
                dbus.Byte('T'), dbus.Byte('e'), dbus.Byte('s'), dbus.Byte('t')
        ]


class CharacteristicUserDescriptionDescriptor(Descriptor):
    
    Writable CUD descriptor.

    
    CUD_UUID = '2901'

    def __init__(self, bus, index, characteristic):
        self.writable = 'writable-auxiliaries' in characteristic.flags
        self.value = array.array('B', b'This is a characteristic for testing')
        self.value = self.value.tolist()
        Descriptor.__init__(
                self, bus, index,
                self.CUD_UUID,
                ['read', 'write'],
                characteristic)

    def ReadValue(self, options):
        return self.value

    def WriteValue(self, value, options):
        if not self.writable:
            raise exceptions.NotPermittedException()
        self.value = value

class TestEncryptCharacteristic(Characteristic):
    
    Dummy test characteristic requiring encryption.

   
    TEST_CHRC_UUID = '12345678-1234-5678-1234-56789abcdef3'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.TEST_CHRC_UUID,
                ['encrypt-read', 'encrypt-write'],
                service)
        self.value = []
        self.add_descriptor(TestEncryptDescriptor(bus, 2, self))
        self.add_descriptor(
                CharacteristicUserDescriptionDescriptor(bus, 3, self))

    def ReadValue(self, options):
        print('TestEncryptCharacteristic Read: ' + repr(self.value))
        return self.value

    def WriteValue(self, value, options):
        print('TestEncryptCharacteristic Write: ' + repr(value))
        self.value = value

class TestEncryptDescriptor(Descriptor):
   
    Dummy test descriptor requiring encryption. Returns a static value.

    TEST_DESC_UUID = '12345678-1234-5678-1234-56789abcdef4'

    def __init__(self, bus, index, characteristic):
        Descriptor.__init__(
                self, bus, index,
                self.TEST_DESC_UUID,
                ['encrypt-read', 'encrypt-write'],
                characteristic)

    def ReadValue(self, options):
        return [
                dbus.Byte('T'), dbus.Byte('e'), dbus.Byte('s'), dbus.Byte('t')
        ]


class TestSecureCharacteristic(Characteristic):
    
    Dummy test characteristic requiring secure connection.

   
    TEST_CHRC_UUID = '12345678-1234-5678-1234-56789abcdef5'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.TEST_CHRC_UUID,
                ['secure-read', 'secure-write'],
                service)
        self.value = []
        self.add_descriptor(TestSecureDescriptor(bus, 2, self))
        self.add_descriptor(
                CharacteristicUserDescriptionDescriptor(bus, 3, self))

    def ReadValue(self, options):
        print('TestSecureCharacteristic Read: ' + repr(self.value))
        return self.value

    def WriteValue(self, value, options):
        print('TestSecureCharacteristic Write: ' + repr(value))
        self.value = value


class TestSecureDescriptor(Descriptor):
   
    Dummy test descriptor requiring secure connection. Returns a static value.

  
    TEST_DESC_UUID = '12345678-1234-5678-1234-56789abcdef6'

    def __init__(self, bus, index, characteristic):
        Descriptor.__init__(
                self, bus, index,
                self.TEST_DESC_UUID,
                ['secure-read', 'secure-write'],
                characteristic)

    def ReadValue(self, options):
        return [
                dbus.Byte('T'), dbus.Byte('e'), dbus.Byte('s'), dbus.Byte('t')
        ]

"""

# Registering our application and creating a gatt server 
def register_app_cb():
    print('GATT application registered')


def register_app_error_cb(mainloop, error):
    print('Failed to register application: ' + str(error))
    mainloop.quit()


def gatt_server_detect_main(mainloop, bus, adapter_name):
	adapter = adapters.find_adapter(bus, GATT_MANAGER_IFACE, adapter_name)
	
	if not adapter:
		raise Exception('GattManager1 interface not found')

	service_manager = dbus.Interface(
		bus.get_object(BLUEZ_SERVICE_NAME, adapter),
		GATT_MANAGER_IFACE)
	
	app = Application(bus)

	print('Registering GATT application...')

	service_manager.RegisterApplication(app.get_path(), {},
                                    reply_handler=register_app_cb,
                                    error_handler=functools.partial(register_app_error_cb, mainloop))

	"""
	# Checks if notify is true. If so, begins the object detection script
	print("We're above the if")
	if app.get_service().get_characteristics()[0]._update_hr_msrmt_simulation():
		print("In here")

		#this is the neural net
		#0.5 baseline
		net = jetson.inference.detectNet("ssd-inception-v2", threshold=0.5)#threshold influences number of objects detected

		#this is the camera object
		#parameters - width, height, device file
		#a good resolution might be 1280*780
		camera = jetson.utils.videoSource("csi://0")

		# Open display to show results  
		display = jetson.utils.videoOutput("display://0")

		# Returns true if display window is still open
		while display.IsStreaming():
			reset_ids()
			
			#return img - blocks until next frame is available
			#converts raw format of the camera to floating point RGBA on the GPU
			img = camera.Capture()
			
			#detectNet object to identify objects
			detections = net.Detect(img)
			
			detected_ids(detections)

			# Gets HeartRateMeasurementChrc and calls the update function on it
			#app.get_service().get_characteristics()[0]._update_hr_msrmt_simulation()
			app.get_service().get_characteristics()[0].hr_msrmt_cb()

			#render overlayed img to the OpenGL window
			display.Render(img)
			
			#update title of window to reflect current performance - uses internal profiling mechanism
			display.SetStatus("Object Detection | Network {:.0f} FPS".format(net.GetNetworkFPS()))
	"""


