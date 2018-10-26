import datetime, re, time, os
UPDATE_TIME_SECONDS = 15
# Email recipients for error report --  currently handles exactly 5 recipients
emailusers = ["Example@domain.com",
              "Example2@domain.com",
              "Example3@domain.com",
              "Example4@domain.com",
              "Example5@domain.com"]
# timers for if instrument is offline
tpt = tco = tti = tgo = tne = tni = ""
instruments = {
    'Cobalt': [tco, r'\\Network_Location\MassLynx\Status.ini'],
    'Platinum': [tpt, r'\\Network_Location_2\Chem32\Status.ini'],
    'Titanium': [tti, r'\\Network_Location_3\Chem32\Status.ini'],
    'Gold': [tgo, r'\\Network_Location_4\MassLynx\Status.ini'],
    'Neon': [tne, r'S:\Network_Location_5\Status.ini'],
    'Nickel': [tni, r'S:\Network_Location_6\Status.ini']
}
MONITOR_HTML_LOCATION = r"S:\Network_Folder\LCMS_monitor.html"
Monitor_OA = r"S:\Network_Folder\LCMS_OA.html"
email = "<br><br><br><i>Report LC/MS problem by <a href=\"mailto:{};{};{};{};{}?" \
        "Subject=LCMS%20Problem%20Report\">e-mail</a></i></center></body></html>".format(emailusers[0], emailusers[1],
                                                                                     emailusers[2], emailusers[3],
                                                                                         emailusers[4])
takeda = r"S:\Network_Folder\takeda_transparent.png"


def color_picker():
    """Colors for background"""
    # Colors change every 3 months
    month = datetime.datetime.now().strftime('%B')
    if month in ("December", "January", "February"):
        one = "B6DFFF"
        two = "97D1FF"
    elif month in ("March", "April", "May"):
        one = "D8F8C4"
        two = "D2F5BD"
    elif month in ("June", "July", "August"):
        one = "FDF6BB"
        two = "FFF6AD"
    else:
        one = "FDCEA3"
        two = "FFC793"
    return one, two


def readfile(file):
    """Import data from instruments"""
    data2 = []
    try:
        ini = open(file, 'r')
        for line in ini.readlines():
            temp = re.sub("[\[\]\\n]", "", line)
            data2.append(temp)
        ini.close()
    except IOError:
        pass
    finally:
        return data2


class instrstatus:
    """Convert raw data to usable data"""
    def __init__(self, inst, summary, mssatus, lcstatus, queue, numsamples, queuelist, color, time, length):
        self.inst = inst
        self.summary = summary
        self.ms = mssatus
        self.lc = lcstatus
        self.q = queue
        self.num = numsamples
        self.qlist = queuelist
        self.color = color
        self.time = time
        self.length = length

    @classmethod
    def offline(cls, instr):
        """Offline instrument status"""
        if instruments[instr][0] == "":
            instruments[instr][0] = datetime.datetime.now().strftime('%H:%M:%S')
            time2 = datetime.datetime.now().strftime('%I:%M:%S %p')
            length = "Now"
        else:
            time = datetime.datetime.now().strftime('%H:%M:%S')
            if int(instruments[instr][0][:2]) < 12:
                time2 = instruments[instr][0] + " A.M."
            else:
                time2 = str(int(instruments[instr][0][:2]) - 12) + instruments[instr][0][2:] + " P.M."
            length2 = datetime.datetime.strptime(time, '%H:%M:%S') - datetime.datetime.strptime(instruments[instr][0],
                                                                                                '%H:%M:%S')
            length = "%s:%s:%s" % (length2.seconds // 3600, (length2.seconds // 60) % 60, length2.seconds % 60)
            length = str(length)
            length += " H:M:S ago"
        status = cls(instr, 'Offline', 'Offline', 'Offline', 'Offline', '', '', 'Red', time2, length)
        return status

    @classmethod
    def instrument(cls, data, instr):
        """Online instrument status"""
        inst = instr
        if instr == "Neon" or instr == "Nickel" or instr == "Cobalt" or instr == "Gold":
            # Lines from raw file with information for MassLynx instruments
            (a, b, c, d, e) = (1, 5, 13, 15, 16)
        else:
            # Lines from raw file with information for MassHunter instruments
            (a, b, c, d, e) = (4, 7, 15, 17, 17)
        running = summary = msstatus = lcstatus = queue = samples = qlist = color = time = time2 = length = ''
        try:
            if data[a] == "Operate=1" or data[a] == "Operate=2":
                msstatus = "OK"
            else:
                msstatus = "Stopped"
            if data[b] == "Status=1":
                lcstatus = "OK"
            elif data[b] == "Status=1":
                lcstatus = "Stopped"
            if data[c] == "Queue Paused=0":
                queue = "OK"
                summary = "Operational"
                color = "Green"
                running = "Acquiring"
                instruments[instr][0] = ""
                length = ""
            elif data[c] == "Queue Paused=1":
                queue = "Paused"
                summary = "Paused"
                color = "Red"
                running = "Paused"
                if instruments[instr][0] == "":
                    # No timer has been saved so the error is occurring now
                    instruments[instr][0] = datetime.datetime.now().strftime('%H:%M:%S')
                    time2 = datetime.datetime.now().strftime('%I:%M:%S %p')
                    length = "Just Now"
                else:
                    # A timer has been set
                    time = datetime.datetime.now().strftime('%H:%M:%S')
                    if int(instruments[instr][0][:2]) < 12:
                        time2 = instruments[instr][0] + " A.M."
                    else:
                        time2 = str(int(instruments[instr][0][:2]) - 12) + instruments[instr][0][2:] + " P.M."
                    length2 = datetime.datetime.strptime(time, '%H:%M:%S') - datetime.datetime.strptime(
                        instruments[instr][0], '%H:%M:%S')
                    length = "%s:%s:%s" % (length2.seconds // 3600, (length2.seconds // 60) % 60, length2.seconds % 60)
                    length = str(length)
                    length += " H:M:S ago"
            if data[d] == "1=No queue" or data[d]=="1=No Queue":
                qlist = "No queue"
            else:
                qlist = data[d][2:data[d].find("Acquiring")] + running
            if e == 16:
                while data[e][:5] != "Total":
                    # The row with the total number of samples in the .ini changes based on the number of people who
                    # have queued runs. This finds that row
                    e += 1
                samplesstart = data[e].find('=')
                samples = data[e][samplesstart + 1:]
            else:
                # Masshunter does not display a total all of the time, so we have to check to see if there is a queue
                if(data[d]) == "1=No Queue" or data[d] == "1=No queue":
                    samples = 0
                else:
                    try:
                        while data[e][:5] != "Total":
                            e += 1
                        samplesstart = data[e].find('=')
                        samples = data[e][samplesstart + 1:]
                    except IndexError:
                        # One masshunter instrument doesn't always show total, so this uses current run as the total
                        sample1 = data[d].find("Samples ")
                        sample1end = data[d].find(" to ")
                        samples1 = data[d][sample1 + 8:sample1end]
                        sample2end = data[d].find(": Sample ")
                        samples2 = data[d][sample1end + 4:sample2end]
                        samples = int(samples2) - int(samples1) + 1
            status = cls(inst, summary, msstatus, lcstatus, queue, samples, qlist, color, time2, length)
        except IndexError:
            # if you can't find all of the relevant info, the instrument is offline
            status = instrstatus.offline(instr)
        return status


def prgrm():
    """generates HTML and uploads it"""
    # background color
    color1 = color_picker()[0]
    color2 = color_picker()[1]
    # Set up HTML header, background
    body = "<!doctype html>\n\n<html lang=\"en\">\n<img src=\"%s\" alt = \"Takeda Logo\"><br><head>\n<title>LCMS" \
           " Monitor</title>\n<meta http-equiv=\"refresh\" " \
           "content=\"15\">\n<style> body {\n\tbackground: radial-gradient(circle,  #ffffff 0%%, #%s 90%%, #%s 100%%)" \
           ";\n\tbackground-color: %s;\n}\n</style>" \
           "</head>\n<body>\n<center>\n<b><u>Oncology Chemistry LC/MS Monitor</b></u><br>\n\n<br>\n\nLast instrument " \
           "check: " \
           "%s\n<br>\n<br>\n<br><b>Open Access Instruments</b>\n<br>\n" \
           % (takeda, color1, color2, color1, datetime.datetime.now().strftime('%A, %b %d at %I:%M:%S %p'))
    # instrument colors
    insts = ['#458EEA','#B8B3B3', '#757574', '#FDBE24','#FF9933', '#B7B7A8']
    id = 0
    for instrument in instruments:
        data = readfile(instruments[instrument][1])
        try:
            # check if file has been updated in the past 2 minutes (instruments set to update every minute)
            os.path.getmtime(instruments[instrument][1])
            if os.path.getmtime(instruments[instrument][1]) < time.time() - (2*60):
                analyzed = instrstatus.offline(instrument)
            else:
                try:
                    analyzed = instrstatus.instrument(data, instrument)
                except ValueError:
                    analyzed = instrstatus.offline(instrument)
        except FileNotFoundError:
            analyzed = instrstatus.offline(instrument)
        # Formulations and end of Open Access version
        if instrument == "Gold":
            body2 = body[:333] + "<br><br><br><br><br><br><br><br><br>" + body[337:]
            body += "<br><br>\n<b>Formulations</b>\n<br>\n"
        # UPLC instruments
        if instrument == "Neon":
            body += "<br><br>\n<b>UPLC Instruments</b>\n<br>\n"
        # If online
        if analyzed.color == "Green":
            color = insts[id]
            body += '<span style="background-color: %s"><br> %s is %s </span><br> LC: %s MS: %s Queue: %s <br>' \
                    'Number of Samples in queue: %s <br>Currently running: %s  <br>\n' % (
            color, instrument, analyzed.summary, analyzed.lc, analyzed.ms, analyzed.q, analyzed.num, analyzed.qlist)
        # If Offline or Paused
        else:
            color = "#E34823"
            body += '<span style="background-color: %s"><br> %s is %s <br> LC: %s MS: %s Queue: %s <br>' \
                    'Number of Samples in queue: %s <br>Currently running: %s  <br>Time of error: %s (%s)</span>\n' % (
                color, instrument, analyzed.summary, analyzed.lc, analyzed.ms, analyzed.q, analyzed.num, analyzed.qlist,
                analyzed.time, analyzed.length)
        id += 1
    body += email
    body2 += email
    # Make HTML files
    file = open(MONITOR_HTML_LOCATION, 'w')
    file.write(body)
    file.close()
    file2 = open(Monitor_OA, 'w')
    file2.write(body2)
    file2.close()


while 1:
    try:
        prgrm()
        time.sleep(UPDATE_TIME_SECONDS)
    except OSError:
        # Sometimes repeated calls to an instrument result in a "Too many remote connections error"
        # This allows the script to keep running instead of erroring out
        # The error resolves itself by the second time around
        pass
