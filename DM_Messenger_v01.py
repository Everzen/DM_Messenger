from PySide import QtCore, QtGui
import sys
import qdarkstyle
import json
from slackclient import SlackClient

#Tempory development token to talk to SVFX-DND-ADVENTURE.slack.com - This validates user DM sending direct messages too! 
slackdevToken = "xoxp-162387755312-163775617798-263442665682-303e123723913ef7c64a5567cfd962f1"  # DM control for SVFX
# slackdevToken = "xoxp-280884692148-281914893415-287653198435-97a41086c515fb1e3aa0af69ecd5f6dc"  # Humble Servant control for DNKnee
# slackdevToken = "xoxp-280884692148-280325517569-287657570707-1ee4b05de3fdb3c8a8f964ba3b053227"  # Dm Control control for DNKnee
# slackdevToken = "xoxp-288684413254-288886548967-288062102037-cd18250efa00223a817c8fd174464a01"  # Humble Servant control for Illumria
# slackdevToken = "xoxp-288684413254-288888280631-287967554916-f69130adfbf2af2fe3871bb018a489b9"  # Dm Control control for Illumria


slack_client = SlackClient(slackdevToken)

jsonFile = 'resources\MessengerData_SVFX.json'
# jsonFile = 'resources\MessengerData_DnKnee.json'
# jsonFile = 'resources\MessengerData_Illumria.json'

tabColumnWidth = 405

def grabInfo(infoType):
    with open(jsonFile) as json_file:
            info = json.load(json_file)
            return info[infoType]


class TabDialog(QtGui.QDialog):
    def __init__(self, fileName, parent=None):
        super(TabDialog, self).__init__(parent)

        tabLayout = QtGui.QVBoxLayout()
        self.tabWidget = QtGui.QTabWidget()
        self.tabWidget.addTab(CommonStatementsTab(), "Common")
        self.tabWidget.addTab(RelativeStatementsTab(), "Relative")
        self.tabWidget.addTab(QuestionsTab(), "Questions")
        self.tabWidget.addTab(QuestSpecificTab(), "Quest Specific")

        tabLayout.addWidget(self.tabWidget)


        userMessageLayout = QtGui.QVBoxLayout()
        userColumnWidth = 150
        userTabWidth = 500
        
        #Setup regarding List - This is going to dictate who the message is about
        regardLabel = QtGui.QLabel("REGARDING:")
        regardingListLW =  QtGui.QListWidget()
        regardingListLW.setMaximumWidth(userColumnWidth)
        regardingList = grabInfo("regardings")

        regardingListLW.insertItems(0, regardingList)

        #set up Message From List
        voiceListLW =  QtGui.QListWidget()
        voiceListLW.setMaximumWidth(userColumnWidth)
        voices =[]

        #Grab all the voices
        voiceLabel = QtGui.QLabel("VOICE ORIGIN:")
        voiceList = grabInfo("voices")
        for text in voiceList:
            voices.append(text["name"])

        voiceListLW.insertItems(0, voices)  
        voiceListLW.setCurrentRow(0)
        voiceListLW.setMaximumHeight(19*len(voices))

        #Setup player List
        playerLabel = QtGui.QLabel("SEND TO PLAYER:")
        playerListLW =  QtGui.QListWidget()
        playerListLW.setMaximumWidth(userColumnWidth)
        players = []

        #Grab all the Players
        playerList = grabInfo("players")
        for text in playerList:
            players.append(text["character"] + " (" + text['name'] + ")")

        playerListLW.insertItems(0, players)
        playerListLW.setMaximumHeight(18*len(players))
        playerListLW.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)

        def findActiveStatement():
        	"""This function returns the listwidget and the selected row in a dictionary"""
        	#Find the list Widget in the Current Tab
        	activeList = self.tabWidget.currentWidget().layout().itemAt(0).widget()
        	# print activeList
        	# print type(activeList)
        	if len(activeList.selectedIndexes()) != 0:
        		# print activeList.selectedIndexes()[0].row()
        		return {'activeListWidget':activeList, "activeStatement" : activeList.selectedIndexes()[0].row()}
        	else:
        		return {'activeListWidget':None, "activeStatement" : None}

        def findActiveRegard():
        	if len(regardingListLW.selectedIndexes()) != 0:
        		# print "Active Regard: " + regardingListLW.item(regardingListLW.selectedIndexes()[0].row()).text()
        		return regardingListLW.item(regardingListLW.selectedIndexes()[0].row()).text()
        	else:
        		return None

        def findActiveVoice():
        	# print "Active Voice: " + str(voiceListLW.selectedIndexes()[0].row())
        	return voiceListLW.selectedIndexes()[0].row()

        def findActivePlayers():
        	activePlayerList = []
        	for index in playerListLW.selectedIndexes():
        		activePlayerList.append(index.row())
        	# print activePlayerList
        	return activePlayerList

        def processMessage():
        	activeStatementDict = findActiveStatement()
        	if activeStatementDict["activeListWidget"]:
        		statement = activeStatementDict["activeListWidget"].item(activeStatementDict["activeStatement"]).text()
        		#Now check if the statement splits - if it does then it requires a regard 
        		splitStatement = statement.split("####")
        		if len(splitStatement) > 1:
        			#The statement has split so collect the regard
        			activeRegard = findActiveRegard()
        			if activeRegard:
        				#Awkard check code to see where we insert the name. If both sections of the split string has characters we insert in the middle. If not we insert on the empty string
        				insertTarget = 2 #this represents the name having to be inserted into the middle
        				for i, splitPhrase in enumerate(splitStatement):
        					if len(splitPhrase) == 0: insertTarget = i
        				#Now we hardcode build the string - messy!
        				if insertTarget == 0:
        					statement = "*" + activeRegard + "*" + splitStatement[1]
        				elif insertTarget == 1:
        					statement = splitStatement[0] + "*" + activeRegard + "*"
        				elif insertTarget == 2:
        					statement = splitStatement[0] + "*" + activeRegard + "*" + splitStatement[1]
        			else: return None
        		return statement
        	else: 
        		return None

        def sendMessage():
        	finalVoice = findActiveVoice()
        	# print "Voice: " + str(finalVoice)
        	finalPlayers = findActivePlayers()
        	# print "Players: " + str(findActivePlayers)
        	finalStatement = processMessage()
        	# print "Statement: " + str(findActiveStatement)
        	# print "My final Statement is: " + str(finalStatement)
        	if (len(finalPlayers) != 0) and finalStatement: #If all if these conditions are met then we should be able to send the message
        		voicename = voiceList[finalVoice]["name"]
        		asUser = int(voiceList[finalVoice]["asUser"])
        		print "Message: " + finalStatement
        		for playerNum in finalPlayers:
        			playerID = playerList[playerNum]["slackID"]
        			slack_client.api_call("chat.postMessage", channel=playerID, text=finalStatement, as_user=asUser, username=voicename )    #Using text to add an emoji
        			print "SENDING TO: " + playerList[playerNum]["character"]
        	else:
        		print "Message failed to SEND"


        sendButton = QtGui.QPushButton("SEND SLACK MESSAGE")
        sendButton.setMinimumHeight(50)
        sendButton.setMaximumWidth(userColumnWidth)
        sendButton.clicked.connect(sendMessage)

        userMessageLayout.addWidget(regardLabel)
        userMessageLayout.addWidget(regardingListLW)
        userMessageLayout.addWidget(voiceLabel)
        userMessageLayout.addWidget(voiceListLW)
        userMessageLayout.addWidget(playerLabel)
        userMessageLayout.addWidget(playerListLW)
        userMessageLayout.addWidget(sendButton)

        mainLayout = QtGui.QHBoxLayout()
        mainLayout.addLayout(tabLayout)
        mainLayout.addLayout(userMessageLayout)

        # mainLayout.addWidget(tabWidget)
        # mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)

        self.setWindowTitle("Dungeon Master - Fast Messenger")



class statementsQLW(QtGui.QListWidget):
    def __init__(self, parent=None):
        super(statementsQLW, self).__init__(parent)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu) #context menu for user data
        self.customContextMenuRequested.connect(self.userMenu)
    
    def userMenu(self, position):
        print (str(self.itemAt(position)))
        menu = QtGui.QMenu()
        if not (self.itemAt(position)): #Test right Click Position - have we hit an item
            menu.addAction(self.tr("Add New Statement"))
        else: 
            menu.addAction(self.tr("Edit Statement"))
            menu.addAction(self.tr("Delete Statement"))
        menu.exec_(self.viewport().mapToGlobal(position))

    def addItems(self, statementList):
        LItems = []
        for text in statementList:
            print (text["statement"])
            newListItem = QtGui.QListWidgetItem((text["statement"]))
            newListItem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
            self.addItem(newListItem)

class CommonStatementsTab(QtGui.QWidget):
    def __init__(self, parent=None):
        super(CommonStatementsTab, self).__init__(parent)

        statementsListBox = statementsQLW()
        statementsListBox.setMinimumWidth(tabColumnWidth)
        statements = []

        #Grab all the common Questions
        commonStatements = grabInfo("CommonStatements")
        print (commonStatements)
        statementsListBox.addItems(commonStatements)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(statementsListBox)
        self.setLayout(layout)


class RelativeStatementsTab(QtGui.QWidget):
    def __init__(self, parent=None):
        super(RelativeStatementsTab, self).__init__(parent)

        statementsListBox = QtGui.QListWidget()
        statementsListBox.setMinimumWidth(tabColumnWidth)
        statements = []

        #Grab all the common Questions
        commonStatements = grabInfo("RelativeStatements")
        for text in commonStatements:
            statements.append(text["statement"])

        statementsListBox.insertItems(0, statements)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(statementsListBox)
        self.setLayout(layout)

class QuestionsTab(QtGui.QWidget):
    def __init__(self, parent=None):
        super(QuestionsTab, self).__init__(parent)

        statementsListBox = QtGui.QListWidget()
        statementsListBox.setMinimumWidth(tabColumnWidth)
        statements = []

        #Grab all the common Questions
        commonStatements = grabInfo("Questions")
        for text in commonStatements:
            statements.append(text["statement"])

        statementsListBox.insertItems(0, statements)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(statementsListBox)
        self.setLayout(layout)


class QuestSpecificTab(QtGui.QWidget):
    def __init__(self, parent=None):
        super(QuestSpecificTab, self).__init__(parent)

        statementsListBox = QtGui.QListWidget()
        statementsListBox.setMinimumWidth(tabColumnWidth)
        statements = []

        #Grab all the common Questions
        commonStatements = grabInfo("QuestStatements")
        for text in commonStatements:
            statements.append(text["statement"])

        statementsListBox.insertItems(0, statements)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(statementsListBox)
        self.setLayout(layout)



if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
	# setup stylesheet
	app.setStyleSheet(qdarkstyle.load_stylesheet())

	if len(sys.argv) >= 2:
	    fileName = sys.argv[1]
	else:
	    fileName = "."

	tabdialog = TabDialog(fileName)
	sys.exit(tabdialog.exec_())



#####################
#  List Widget Items .... self.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)