import subprocess
import os
import json
from jira import JIRA
from datetime import datetime
import shutil

# for testing locally
# os.environ["test_case"] = "stage"
#  --------------

repo_name = "testing_selenium"

cmd = "git clone https://github.com/pelos/{0}.git".format(repo_name)
p1 = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
out, err = p1.communicate()
print(out.decode())
print(err.decode())
p1.stdout.close()

# print("file dirs structure:")
# for subdir, dirs, files in os.walk(os.getcwd()):
#     for filename in files:
#         filepath = subdir + os.sep + filename
#         print(filepath)
# print("")
print("os.getcwd()")
print(os.getcwd())

tt = "{0} \nTests:\n".format(datetime.now())

test_to_execute = []
parent = os.path.abspath(os.getcwd())
print("os.listdir(parent)")
print(os.listdir(parent))
repo_folder = os.path.abspath(os.path.join(parent, repo_name))
print("os.listdir(repo_folder)")
print(os.listdir(repo_folder))
test_to_run_folder = "tests_to_run"
test_folder = os.path.abspath(os.path.join(repo_folder, test_to_run_folder))
print("os.listdir(test_folder)")
print(os.listdir(test_folder))

json_file = os.path.abspath(os.path.join(test_folder, "test_organization.jsonc"))
print(json_file)
print("json_file exists: {0}".format(os.path.isfile(json_file)))


try:
    with open(json_file) as f:
        data = json.load(f)
        data[os.environ["test_case"]]
        case = data[os.environ["test_case"]]
        test_to_execute = case
except:
    print("we didnt find that test_case set")
    print("we are going to use {0}".format(os.environ["test_case"]))
    if os.environ["test_case"].endswith(".py") is False:
        raise ValueError("single test_case doesnt end with .py")
    test_to_execute.append(os.environ["test_case"])


print("Test from '{0}' to_execute:".format(os.environ["test_case"]))
for i in test_to_execute:
    print(i)
print("-----------------------------")

# create a new folder and move the tests scripts there
temp_test_runner_folder = os.path.abspath(os.path.join(repo_folder, "temp_test_runner"))
print("Creating a new temporary folder: {0}".format(temp_test_runner_folder))
os.mkdir(temp_test_runner_folder)


logger_file = open("logger_file.log", "w+")
for i in test_to_execute:
    tt = tt + i + "\n"
    path_to_file = os.path.abspath(os.path.join(test_folder, i))
    print("Test file: {0}  exists: {1}".format(path_to_file, os.path.isfile(path_to_file)))
    shutil.copy(path_to_file, temp_test_runner_folder)

# the flow cli  use the folder doesnt run the test individualy we might change the subprocess to not be a loop
for i in os.listdir(temp_test_runner_folder):
    path_to_temp_file = os.path.abspath(os.path.join(temp_test_runner_folder, i))
    cmd = "pytest {0}".format(path_to_temp_file)
    p1 = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, err = p1.communicate()
    print(out.decode())
    print(err.decode())
    logger_file.write(out.decode())
    logger_file.write(err.decode())
    p1.stdout.close()
logger_file.close()

print("Deleting temp folder: {0}".format(temp_test_runner_folder))
shutil.rmtree(temp_test_runner_folder)

print("Deleting repo folder: {0}".format(repo_folder))
shutil.rmtree(repo_folder, ignore_errors=True)


JIRA_SERVER = os.environ["jira_server"]
USER = os.environ['user']
TOKEN = os.environ['token']

jira = JIRA(server=JIRA_SERVER, basic_auth=(USER, TOKEN))
issue = jira.issue(os.environ["jira_text_execution"])
print("this is the issue: {0}  issue_id:{1}".format(issue, issue.id))

logger_file = open("logger_file.log", "r")

tt = tt + "Results:\n"
file_lines = logger_file.readlines()
for i in file_lines:
    if i != "\n":
        # print(i)
        tt = tt + i
# print(file_lines)
comment = jira.add_comment(issue, tt)
logger_file.close()


print("\ntesting_selenium_folder directory:")
print(os.listdir(repo_folder))
print(os.path.isdir(repo_folder))
shutil.rmtree(repo_folder, ignore_errors=True)
print("testing_selenium_folder deleted")
