import sublime, sublime_plugin
import os
from subprocess import *

class FilenameToClipboardCommand(sublime_plugin.TextCommand):
	def run(self, edit):

		file_name = sublime.active_window().active_view().file_name()

		if file_name is not None:
			sublime.set_clipboard(file_name)
			sublime.message_dialog("Copied to clipboard %s\n" % file_name)

	def description(self):
		return "Copy tab filename to clipboard"