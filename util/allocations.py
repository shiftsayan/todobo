import random, math
import gradescope

from secrets import GRADESCOPE_COURSE_ID

def get_most_recent_homework():
    assignments = gradescope.get_course_assignments(GRADESCOPE_COURSE_ID)
    return max(assignments, key=lambda x: 0 if 'Homework' not in x['name'] else int(x['name'].split(' ')[-1]))

def get_named_assignment(name):
    assignments = gradescope.get_course_assignments(GRADESCOPE_COURSE_ID)
    return [i for i in assignments if i['name'] == name][0]

def get_num_submissions(hw_id):
    grades = gradescope.get_assignment_grades(GRADESCOPE_COURSE_ID, hw_id)
    return sum(1 if student['Status'] != 'Missing' else 0 for student in grades)

def get_allocations_for_question(total, graders):
    grader_map = {}
    need_grader = []
    total_already_assn = 0

    for grader in graders:
        if '(' in grader:
            try:
                total_already_assn += int(grader[grader.index('(')+1:grader.index(')')])
                grader_map[grader.split('(')[0].strip()] = int(grader[grader.index('(')+1:grader.index(')')])
            except:
                need_grader.append(grader)
        else:
            need_grader.append(grader)

    if total_already_assn > total:
        return "Too many preassigned graders!"

    split_len = math.ceil((total - total_already_assn) / len(need_grader))
    random.shuffle(need_grader)
    for grader in need_grader[:-1]:
        grader_map[grader] = split_len

    grader_map[need_grader[-1]] = total - total_already_assn - (len(need_grader) - 1) * split_len

    gs = list(grader_map.keys())
    curr = 0
    random.shuffle(gs)
    ans = []

    for g in gs:
        ans.append(f"{g} ({curr+1}-{curr+grader_map[g]})")
        curr += grader_map[g]

    return ', '.join(ans)

def assemble_question_info(question, total):
    graders = question['graders']
    return f"{question['name']}: {get_allocations_for_question(total, graders)}"

def get_allocations(message):
    message_lines = message.split('\n')

    if len(message_lines) < 2:
        return

    allocation_lines = [i+1 for i, line in enumerate(message_lines[1:]) if ':' in line]

    current_assignment = get_most_recent_homework() if '[' not in message_lines[0] else get_named_assignment(message_lines[0][message_lines[0].index('[')+1:message_lines[0].index(']')])
    num_submissions = get_num_submissions(current_assignment['id'])
    assignment_name = current_assignment['name']

    questions = []
    for line in allocation_lines:
        txt = message_lines[line].split(':')
        if len(txt) != 2:
            continue
        questions.append({
            'name': txt[0],
            'graders': [i.strip() for i in txt[1].split(',')]
        })

    allocations = f"Grader splits for {assignment_name}:\n"
    allocations += '\n'.join(assemble_question_info(q, num_submissions) for q in questions)

    return allocations