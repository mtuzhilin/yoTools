import sublime, sublime_plugin
import os
from subprocess import *

class YoYiicWorkersCommand(sublime_plugin.TextCommand):
	workers = []
	def run(self, edit):
		if 0 == len(self.workers):
			f = open(settings().get("workers_list"), "r")
			workers_list = f.readlines()
			f.close()
			for worker in workers_list:
				worker = worker[34:worker.find("|")].strip()
				if len(worker) > 0:
					self.workers.append(worker)

		running_workers = os.popen("ps -ax | grep [A]mqp").readlines()


		for worker in running_workers:
			index = running_workers.index(worker)
			worker = worker[worker.find("Amqp")+1:]
			worker = worker[worker.find("Amqp"):].strip()

			running_workers[index] = worker

		menu_items = []

		for worker in self.workers:

			if worker in running_workers:
				menu_items.append([worker, "running"])
			else:
				menu_items.append([worker, "stopped"])




		self.view.window().show_quick_panel(menu_items, self.on_click)

	def on_click(self, index):
		if -1 == index:
			return
		# print(self.workers)
		worker = self.workers[index]


		if not self.is_process_running(worker):
			sublime.status_message("starting %s" % worker)
			cmd = ("%s daemon start AmqpWorkerSupervisor %s" % (settings().get("yiic"), worker))
			pipe = Popen(cmd.split(" "), stdout = PIPE, stderr = PIPE)

			poll_result = pipe.poll()

			if not self.is_process_running(cmd):
				sublime.error_message("Something went wrong while starting %s, see log or try to start it manually" % worker)
			else:
				sublime.message_dialog("%s started" % worker);
		else:
			sublime.status_message("stopping %s" % worker)
			cmd = ("%s daemon stop AmqpWorkerSupervisor %s" % (settings().get("yiic"), worker))

			pipe = Popen(cmd.split(" "), stdout = PIPE, stderr = PIPE)

			result = pipe.communicate()
			stdout = result[0].decode("utf-8")
			stderr = result[1].decode("utf-8")

			if self.is_process_running(cmd) or "" != stderr:
				sublime.error_message(
"""Something went wrong while stopping %s, see log or try to stop it manually.
Standart out:
%s
Standart error:
%s
""" % (worker, stdout, stderr))
			else:
				sublime.message_dialog("%s stopped" % worker);
# Show error about this problem in future?

	def is_process_running(self, cmd):
		p1 = Popen(["ps", "-ax"], stdout = PIPE, stderr = PIPE, universal_newlines = True)
		first_letter = cmd[0:1]
		cmd = cmd.replace(first_letter, "[" + first_letter + "]", 1)
		# cmd = "'" + cmd + "'"
		p2 = Popen(["grep", cmd],
			stdin = p1.stdout, stdout = PIPE, stderr = PIPE, universal_newlines = True)
		p1.wait()

		ps_result = p2.communicate()
		ps_stdout = ps_result[0].strip()
		ps_stderr = ps_result[1].strip()

		if len(ps_stderr) > 0:
			sublime.error_message("Error possible when executing worker\ncmd: \n%s\nps:\n%s" % (cmd, ps_stderr))

		# тут мы проверяем, что он запустился и что он именно один

		if "" == ps_stdout:
			return False


		return 1 == len(ps_stdout.split("\n"))

	def description(self):
		return "Start/Stop Yii workers"

def settings():
	if settings.settings is None:

		file_path = sublime.packages_path() + "/User/"
		file_name = "yoTools.sublime-settings"

		settings.settings = sublime.load_settings(file_name)

		required_keys = ["yiic", "workers_list"]

		good_config = True
		for key in required_keys:
			if settings.settings.get(key) is None:
				settings.settings.set(key, None)
				good_config = False

		if not good_config:
			sublime.save_settings(file_name)
			sublime.active_window().open_file(file_path + file_name)
			settings.settings = None
			return

	return settings.settings

settings.settings = None

def call(args):
	# print(os.getcwd())
	if type(args) == str:
		args = args.split(" ")


	result = subprocess.Popen(args, stdout = subprocess.PIPE, stderr = subprocess.PIPE, universal_newlines = True).communicate()
	error = result[1]
	result = result[0]

	return result

