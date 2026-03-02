import wmi

c = wmi.WMI()
for disk in c.Win32_DiskDrive():
    if 'USB' in disk.InterfaceType:
        #print(f"Device: {disk.Caption}")
        #print(f"Serial Number: {disk.SerialNumber.strip()}")
        #print("---------")
