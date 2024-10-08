import dash
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, MATCH, ALL
import random
from glob import glob
import json
import argparse
# from create_start_state import reset_json_file
import random
import sys
from time import perf_counter
from datetime import date
import os
import signal
import pandas as pd






initial_state_18 = [0 for i in range(18)]
card_id = -1


# =========CLI Parsing===============
arg_container = argparse.ArgumentParser(description='Specify the Operating System')

# should be optional arguments container.add_arguments
arg_container.add_argument('--is_os_win', '-Is_Operating_System_Windows', type=int, required=True,
                           help='Is your OS Windows? (--os True) else False')

arg_container.add_argument('--initials', "-Annotator's_name_initials", type=str, required=True,
                           help='example: if your name is Prateek Pani, type "--initials pp"')

args = arg_container.parse_args()
# ====================================






# paths_of_images = glob('static/pool_Set/*.jpg')
if args.is_os_win == 0:
    paths_of_images = glob('static/Test_Set/*.png')
else:
    paths_of_images = glob('static\\Test_Set\\*.png')
    #print(paths_of_images)







# print(paths_of_images[0])
class_of_all_images = [-1] * len(paths_of_images)  # stores the class annotations of all the images by initialising -1.s
print('paths_of_images\n', paths_of_images)


# =========== globRead_idx_file_name_maps ==============================
def globRead_idx_file_name_maps(image_paths):
    '''Need to verify for WIndows and Non-Win'''

    ordered_file_name_list = []
    for i in range(len(image_paths)):
        for j in range(len(image_paths)):

            if args.is_os_win == 0:
                k = image_paths[j].split('/')[-1].split('__')[0]
                if int(k) == int(i):
                    ordered_file_name_list.append(image_paths[j].split('/')[-1])
                    break

            elif args.is_os_win == 1:
                k = image_paths[j].split('\\')[-1].split('__')[0]
                if int(k) == int(i):
                    ordered_file_name_list.append(image_paths[j].split('\\')[-1])
                    break
            
            

    return ordered_file_name_list

ordered_file_name_list = globRead_idx_file_name_maps(paths_of_images)
# temp = []

# ordered_file_name_set = set(ordered_file_name_list)
# for i in range(len(ordered_file_name_list)):
#     for se in ordered_file_name_set:
#         if se.startswith(f'{i}__'):
#             temp.append(se)
#             break

# ordered_file_name_list = temp
# print(ordered_file_name_list)
# print(ordered_file_name_list) #['0__2672632_21015_0_0.png', '1__1146137_21015_1_0.png',...
                                #  '179__3865278_21015_0_0.png']
# Use ordered_file_name_list instead of paths_of_images and check association

# =========== globRead_idx_file_name_maps ==============================













today = date.today()
day, month, year = date.today().day, date.today().month, date.today().year
name_initials = args.initials

if args.is_os_win == 0:
    path = './StatsIO/{}/{}_{}_{}/session_num.json'.format(name_initials, day, month, year)
    my_file = open(path, "r")
    session_dict = json.loads(my_file.read())   
    session_num = session_dict['session_num'] 

else:
    path = '.\\StatsIO\\{}\\{}_{}_{}\\session_num.json'.format(name_initials, day, month, year)
    my_file = open(path, "r")
    session_dict = json.loads(my_file.read()) 
    session_num = session_dict['session_num'] 


print("\nsession_num\n",session_num)


def modify_session_file_for_the_day(session_num):
    today = date.today()
    day, month, year = date.today().day, date.today().month, date.today().year
    name_initials = args.initials

    if args.is_os_win == 0:
        path = './StatsIO/{}/{}_{}_{}/session_num.json'.format(name_initials, day, month, year)
        fp = open(path, "w")
        session_num += 1
        d = {'session_num': session_num}
        fp.write(json.dumps(d))

    else:
        path = '.\\StatsIO\\{}\\{}_{}_{}\\session_num.json'.format(name_initials, day, month, year)
        fp = open(path, "w")
        session_num += 1
        d = {'session_num': session_num}
        fp.write(json.dumps(d))


def read_sess_file():
    if args.is_os_win == 0:
        path = './StatsIO/{}/{}_{}_{}/session_num.json'.format(name_initials, day, month, year)
        fp = open(path, "r")
        d = json.load(fp)
        return int(d["session_num"])

    else:
        path = '.\\StatsIO\\{}\\{}_{}_{}\\session_num.json'.format(name_initials, day, month, year)
        fp = open(path, "r")
        d = json.load(fp)
        return int(d["session_num"])
        




# ===========global variables==========================
unseen_idx_set = set({})
unseen_idx_set_start = set({})
unseen_idx_list = []
gl_state_18 = []
gl_current_18 = []
state_18 = []
current_18 = []
batch_start_time = 0
batch_end_time = 0
glob_idx = [i for i in range(len(paths_of_images))]
time_logs = []
plot_grid_session_iter_num = 0


# ===========global variables==========================


def calculate_ann_time(batch_start_time, save_to_disk=False):
    global time_logs
    global session_num

    batch_end_time = perf_counter()
    time_elapsed = batch_end_time - batch_start_time
    time_logs.append(time_elapsed)

    if save_to_disk == True:
        if args.is_os_win == 0:
            path = './StatsIO/{}/{}_{}_{}'.format(name_initials, day, month, year)
            file_name = f"time_logs_{session_num}.json"
            fp = open(os.path.join(path, file_name), 'w')
            d = {'time_logs': time_logs}
            fp.write(json.dumps(d))
        else:
            path = '.\\StatsIO\\{}\\{}_{}_{}'.format(name_initials, day, month, year)
            file_name = f"time_logs_{session_num}.json"
            fp = open(os.path.join(path, file_name), 'w')
            d = {'time_logs': time_logs}
            fp.write(json.dumps(d))


    return batch_end_time, time_elapsed


def check_point():
    '''function reads the last_checkpoint file and returns the current iter_no'''
    with open(f'last_checkpoint_{args.initials}.txt') as lc:
        iter_no = lc.read()
    lc.close()
    iter_no = int(iter_no)
    return iter_no


iter_no = check_point()
sess_start_iter_no = iter_no
print('New Session Resuming from iteration: {}'.format(iter_no))

# =============create folder for a particular session per person per day============================
name_initials = args.initials  # Use this to make folders
today = date.today()
day, month, year = date.today().day, date.today().month, date.today().year

def create_folder(today, name_initials):
    '''Should create a folder if not present and if present print'''
    day, month, year = today.day, today.month, today.year
    if args.is_os_win == 0:
        path = './StatsIO/{}/{}_{}_{}'.format(name_initials, day, month, year)
    else:
        path = '.\\StatsIO\\{}\\{}_{}_{}'.format(name_initials, day, month, year)
    # os.makedirs(path)
    try:
        os.makedirs(path)
        print("Directory created successfully")
    except OSError as error:
        print("Directory already present")


create_folder(today, str(name_initials))


# =============xxxx particular session xxxx============================
# jpg

# data retrieval for states
def read_json(today, ordered_file_name_list):
    global class_of_all_images
    global paths_of_images
    day, month, year = today.day, today.month, today.year

    pool_idx_list = list(range(len(paths_of_images)))
    gn_list, hk_list, gv_list = [], [], []
    hk_dict, gn_dict, gv_dict = {}, {}, {}
    hk_list = []
    hk_dict = {}

    # hk_list = [idx for idx in range(len(paths_of_images))]
    hk_list = ordered_file_name_list



    if args.is_os_win == 0:
        with open(f"StatsIO/{args.initials}/{day}_{month}_{year}/yest_inp_file.json", 'r') as f:  # change here only for the initials from folder @every start of session
            m = json.loads(f.read())
            if args.initials == 'hk':
                for i in range(len(hk_list)):
                    class_of_all_images[i] = int(m[str(hk_list[i])])
            elif args.initials == 'gv':
                for le in gv_list:
                    class_of_all_images[int(le)] = int(m[f'img_{le}.png'])
            elif args.initials == 'gn':
                for le in gn_list:
                    class_of_all_images[int(le)] = int(m[f'img_{le}.png'])
            else:
                raise KeyboardInterrupt


    else:
        with open(f"StatsIO\\{args.initials}\\{day}_{month}_{year}\\yest_inp_file.json", 'r') as f:  # change here only for the initials from folder @every start of session
            m = json.loads(f.read())
            if args.initials == 'hk':
                for i in range(len(hk_list)):
                    class_of_all_images[i] = int(m[str(hk_list[i])])

            elif args.initials == 'gv':
                for le in gv_list:
                    class_of_all_images[int(le)] = int(m[f'img_{le}.png'])
            elif args.initials == 'gn':
                for le in gn_list:
                    class_of_all_images[int(le)] = int(m[f'img_{le}.png'])
            else:
                raise KeyboardInterrupt



read_json(today, ordered_file_name_list)


# start of session reads from your_file.txt for unseen_idx_set
def start_new_session():
    global unseen_idx_set
    global paths_of_images
    global unseen_idx_list
    global unseen_idx_set_start
    global session_start_time
    global plot_grid_session_iter_num

    plot_grid_session_iter_num = 0

    my_file = open(f"your_file_{args.initials}.txt", "r")
    content = my_file.read()
    if len(list(content)) == 0:
        unseen_idx_set = set([i for i in range(len(paths_of_images))])
        unseen_idx_list = list(unseen_idx_set)
    else:
        ssi = list(content.split('\n'))
        ssi = [int(le) for le in ssi if le != '']
        unseen_idx_set_start = set(ssi)
        unseen_idx_set = set(ssi)
        unseen_idx_list = list(unseen_idx_set)

    #print(unseen_idx_list) 


start_new_session()

def save_functionality(ordered_file_name_list):
    '''On Clicking save save (1)recordings into mnist_data.json,
    (2)save unseen idx already calculated in its next call into your_file.txt'''

    global iter_no
    global class_of_all_images
    global unseen_idx_set
    global state_18
    global current_18
    global gl_state_18
    global gl_current_18

    current_18 = list(unseen_idx_set)[:18]

    m = {}

    #   modify class_of_all_images before writing
    for i in range(len(gl_current_18)):
        class_of_all_images[gl_current_18[i]] = gl_state_18[i]

    # ======= saving everything in datastructures i.e MM i.e RAM for now as a session is to be treated as an atomic event =================
    # req_dict = {f'img_{i}.png': class_of_all_images[i] for i in range(len(class_of_all_images))}
    req_dict = {str(ordered_file_name_list[i]): class_of_all_images[i] for i in range(len(class_of_all_images))}


    unseen_idx_set = unseen_idx_set.difference(set(current_18))
    ssil = list(unseen_idx_set)

    print('\nEOSAVE')
    # print(c1)
    return ""




# ======================================================================= dash app ====================================
# ========================================================================================================================================================================


# ============ In card_body() we initialize the placeholder values from the previous_day json-file ================
def card_body(card_id):
    global current_18
    global state_18
    global paths_of_images
    global class_of_all_images
    global ordered_file_name_list
    # static/Test_Set/99__2194715_21015_1_0.png


    for i in range(len(current_18)):
        if current_18[i] == card_id:
            break

    #============= CHANGES HERE CHANGES THE HEIGHT AND WIDTH OF INDIVIDUAL IMAGE EMBEDDED IN A CARD.================
    # className=f'img_{card_id}', 
 # dbc.CardImg(id = f'cardimg_id_{card_id}', src=paths_of_images[card_id] ,  top=True, style={"height": "125px", "width": "188px"}, n_clicks=0),
    # make changes to CardImg here the img will sit.
    print(f'From card_body: {ordered_file_name_list[card_id]}, card_id: {card_id} \n')

    if args.is_os_win == 0:
        src = f"static/Test_Set/{ordered_file_name_list[card_id]}"
    else:
        src = f"static\\Test_Set\\{ordered_file_name_list[card_id]}"

    return [
        html.Div(
                dbc.CardImg(src=src ,  
                            top=True, 
                            style={"height": "125px", 
                                    "width": "160px",
                                    'z-index':'3'}, 
                            id = {'type':'CardImg', 'index':f'{card_id}'} 
                            ),
                n_clicks=0, 
                id = {'type':'CardDiv', 'index':f'{card_id}'}, 
                title=f"{ordered_file_name_list[card_id]}"
                ),

        dbc.CardBody(
                [
                    dcc.RadioItems
                    (
                        id={
                            'type': 'label-option',
                            'index': "{}".format(card_id)  # global ids
                        },
                        options=[

                                    {'label': 'Normal', 'value': "0"},
                                    {'label': 'Poor Quality', 'value': "1"},
                                    {'label': 'Unsure', 'value': "2"},
                                    {'label': 'Hypo', 'value': "3"},
                                    {'label': 'Abnormal', 'value': "4"}
                                ],
                        value=str(state_18[i]),
                        labelStyle={'display': 'inline-block', 
                                    "padding": "0px 1px 0px 1px", 
                                    "margin": "1px", 
                                    'fontsize':'1px'},
                        inputStyle={"margin-right": "1px"},
                        className=""
                    )
                ], 
            style={"padding": "0.05rem"})
    ]

# make changes here to get reflected in each rectangle(card) as a whole
def card(card_id):
    global current_18
    title = "title"
    description = "desc"
    return html.Div(card_body(card_id), id = {
        'type': 'btncard',
        'index': "{}".format(card_id)  # global ids
            },
        style={"height": "210px", "width": "200px"},
        n_clicks=0
        )
# children=html.Img(className='icon') 
# className=f'img_{card_id}'


app = dash.Dash(
    __name__,
    assets_folder='./assets',
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}],
    )


    # assets_folder='./assets'


# change styling of buttons
app.layout = html.Div(
    [
    html.Button("Start Annotation", id="start-session", n_clicks=0,
                style={'textAlign':'center','margin':'auto', 'backgroundColor': "Green", "color": "green", "margin": "5px", "padding": "5px", "display":'block'}),

    html.Button("Next", id="next", n_clicks=0,
                style={'textAlign':'center','margin':'auto', 'backgroundColor': "blue", "color": "white", "margin": "5px", "padding": "5px", "display":"none"}),

    html.Button("Stop Session", value='Stop Session', n_clicks=0, id="stop-session",
                style={'textAlign':'center','margin':'auto', 'backgroundColor': "Tomato", "color": "white", "margin": "5px", "padding": "5px", "display":"none"}),

    html.Div(id="card-deck",   

             style={"margin": "1px", "padding": "1px" , "display":"block"}),

    html.H3(id='button-clicks'),
    ], 

    style={'text-align': "center", "margin": "0.5em 0em"}
    )


def gen_cards(current_18,  no_func=False):

    if no_func == True:
        return []

    global gl_state_18
    global gl_current_18
    gl_current_18 = current_18
    gl_state_18 = state_18

    return [
        dbc.Row([
            dbc.Col([card(i)]) for i in gl_current_18[:6]]),
        dbc.Row([
            dbc.Col([card(i)]) for i in gl_current_18[6:12]]),
        dbc.Row([
            dbc.Col([card(i)]) for i in gl_current_18[12:18]]),
    ]


def predict_next_18_states(next_18):
    '''invoked from next i.e when "next_btn" is clicked and Uses ML to predict
    placeholders for next set of 18 points.....for now placeholders follow the following logic

    Here, I already have 18_predicted states predicted by model "yesterday" in yesterday_file. Just read the file and
    associate |yesterday_set|//3 inp-labels.json and assign to state_18'''
    global state_18
    global class_of_all_images

    state_18 = [class_of_all_images[int(le)] for le in next_18]
    return state_18


def most_confused_18():
    '''invoked from next ; calculates most confused 18 images based on HITL....
    for now random 18 from unseen_idx_set

    Here, I already have 18_predicted indices predicted by model "yesterday" in yesterday_file. Just read the file and
    associate |yesterday_set|//3 inp-labels.json and assign to next_18'''
    global unseen_idx_set
    global class_of_all_images

    # read file here now I have deterministically (|yesterday_set|//3) idxs Of the "new_indices" put batches of 18 here.
    next_18 = list(unseen_idx_set)[:18]

    return next_18



def write_onto_df(images_annotated_today_dict):
    key_list = []
    value_list = []
    df_dict = {'image_name': [], 'label': []}
    for key,value in images_annotated_today_dict.items():
        df_dict['image_name'].append(key)
        df_dict['label'].append(value)

    df = pd.DataFrame.from_dict(df_dict)
    return df





# ============== Save Labels Uptil Now ==========================================
def save_labels_uptil_now(n_images, ordered_file_name_list):
    '''Only on clicking i.e n_clicks>=1 export button would work not from starting when the app runs'''
    global batch_start_time

    batch_start_time, time_elapsed = calculate_ann_time(batch_start_time, save_to_disk=True)

    global iter_no
    global class_of_all_images
    global unseen_idx_set
    global state_18
    global current_18
    global gl_state_18
    global gl_current_18
    global name_initials
    global today
    global unseen_idx_set_start
    global session_num
    

    day, month, year = today.day, today.month, today.year
    current_18 = list(unseen_idx_set)[:18]


    m = {}

    #   modify class_of_all_images before writing
    for i in range(len(gl_current_18)):
        class_of_all_images[gl_current_18[i]] = gl_state_18[i]

    # ======= saving everything in datastructures i.e MM i.e RAM for now as a session is to be treated as an atomic event =================
    # req_dict = {f'img_{i}.png': class_of_all_images[i] for i in range(len(class_of_all_images))}
    req_dict = {str(ordered_file_name_list[i]): class_of_all_images[i] for i in range(len(class_of_all_images))}


    unseen_idx_set = unseen_idx_set.difference(set(current_18))
    ssil = list(unseen_idx_set)

    # =======================================================================================================================================

    # ================ saving everything in secondary memory (Disk) at StatsIO/{initials}/{day_month_year} ==========================================================================
    # create a dict1 and dump here. How to create idx from class_of_all_images and from index we know the img_name?

    # ======== save o/p files ===============================
    if args.is_os_win == 0:
        with open(file='./StatsIO/{}/{}_{}_{}/mnist_uptil_today_out_files.json'.format(name_initials, day, month, year),  mode="w") as f:
            f.write(json.dumps(req_dict))

    else:
        with open(file='.\\StatsIO\\{}\\{}_{}_{}\\mnist_uptil_today_out_files.json'.format(name_initials, day, month, year),  mode="w") as f:
            f.write(json.dumps(req_dict))


    # save the idx_unseen uptil now
    with open(f'your_file_{args.initials}.txt', 'w') as f:
        for item in ssil:
            print(item)
            f.write("%s\n" % item)

    # save the last_checkpoint for this user so as to start from correct point the next time
    iter_no += 1
    file1 = open(f"last_checkpoint_{args.initials}.txt", "w")
    file1.write('{}'.format(str(iter_no)))
    file1.close()


    # create the idx-state file annotated_today
    my_file = open(f"your_file_{args.initials}.txt", "r")
    content = my_file.read()
    ssi = list(content.split('\n'))
    ssi = [int(le) for le in ssi if le != '']
    unseen_idx_set_next = set(ssi)
    idx_set_annotated_today = unseen_idx_set_start.difference(unseen_idx_set_next)
    # images_annotated_today_dict = {f'img_{int(idx)}.png': req_dict[f'img_{int(idx)}.png'] for idx in idx_set_annotated_today}
    images_annotated_today_dict = { str(ordered_file_name_list[ int(idx) ]) : req_dict[ str(ordered_file_name_list[int(idx) ]) ] for idx in idx_set_annotated_today}

    sess_now_idx = read_sess_file()

    # write onto json and DataFrame file
    if args.is_os_win == 0:
        with open(file='./StatsIO/{}/{}_{}_{}/images_annotated_today_{}.json'.format(name_initials, day, month, year, session_num),mode="w") as f:
            f.write(json.dumps(images_annotated_today_dict))
        # save DataFrame
        df = write_onto_df(images_annotated_today_dict)
        df.to_csv('./StatsIO/{}/{}_{}_{}/images_annotated_today_{}.csv'.format(name_initials, day, month, year, (sess_now_idx) ) )
        

    else:
        with open(file='.\\StatsIO\\{}\\{}_{}_{}\\images_annotated_today_{}.json'.format(name_initials, day, month,year, session_num), mode="w") as f:
            f.write(json.dumps(images_annotated_today_dict))
        # save DataFrame
        df = write_onto_df(images_annotated_today_dict)
        df.to_csv('.\\StatsIO\\{}\\{}_{}_{}\\images_annotated_today_{}.csv'.format(name_initials, day, month,year, (sess_now_idx) ) )
        
    


    print(f'\n{(1 - (len(unseen_idx_set)/int(n_images))) *100:.1f}% of the images parsed\n')
    print('\nBatch of 90 images successfully saved to disk!!\n')

    # Use the following in a button functionality based on the user input last part of the functionality
    # os.kill(os.getpid(), signal.SIGTERM)

    return ""

# ============== End of Save Labels Uptil Now ==========================================





# ============== Start Session ============================================
@app.callback(
    [
    Output(component_id='start-session', component_property='style'),
    Output(component_id='next', component_property='style') ],
    # Output(component_id='export', component_property='style')   ],
    Input(component_id="start-session", component_property="n_clicks"),
    prevent_initial_call = False
)
def start_session(n_clicks):
    print('\nInside START Session\n')

    print('start',n_clicks)

    # {"display":'none'}
    if n_clicks == 0:
        return [{'textAlign':'center','margin':'auto', 'backgroundColor': "green", "color": "white", "display":'block'},
                {"display":'none'},
                ]

    # {"display":'none'}
    if n_clicks == 1:
        return [{"display":'none'},
                {'textAlign':'center','margin':'auto', 'backgroundColor': "blue", "color": "white", "padding": "5px", "display":'block'},
                 ]
 

 # ============== End of Start Session ============================================



# Output('next', 'style'),
#     Output('export', 'style')
@app.callback(
    [
        Output('card-deck', 'children'),
        Output('card-deck', 'style'),
        # Output('next', 'style'),
        Output('stop-session', 'style')
     ],
    Input("next", "n_clicks"),
    prevent_initial_call=True

)
def next(n_clicks):
    '''calculates next set of 18 indices and assigns placeholders to these before loading
    invoke most_confused_18 and then predict_next_18_states'''
    global ordered_file_name_list
    global class_of_all_images
    global unseen_idx_set
    global current_18
    global state_18
    global iter_no
    global paths_of_images
    global batch_start_time
    global batch_end_time
    global plot_grid_session_iter_num
    global initial_state_18




    if( (n_clicks % 6 == 0) ):
        print(f"\nNext is clicked: {n_clicks}th time; Session_num: {session_num}\n")
        save_labels_uptil_now(len(paths_of_images), ordered_file_name_list)
        # return [gen_cards(current_18, no_func=True), 
        #         {'display':'none'}, 
        #         # {'display':'none'}, 
        #         {'textAlign':'center','margin':'auto', 'backgroundColor': "Tomato", "color": "black", "padding": "5px", "display":'block'}]
        return []
    
    # reset initial_state_18 i.e for the initial_states of button-n_clicks for radiobuttons
    # when n_clicks (next) %6 !=0

    initial_state_18 = [0 for i in range(18)]
    plot_grid_session_iter_num += 1
    if plot_grid_session_iter_num >= 2:
        save_functionality(ordered_file_name_list)
    # Only save the logs in MM not to disk yet
    batch_start_time, time_elapsed = calculate_ann_time(batch_start_time, save_to_disk=True) #inside this fn def per_counter


    if int(iter_no) < ((1000 // 18) + 1):
        current_18 = most_confused_18()  # next_24 will be current_24 for next iter
        state_18 = predict_next_18_states(current_18)  # returned state list of these current_24 points

    #   {'display':'none'}, {'display':'none'},
    return [gen_cards(current_18), 
            {'display':'block'},  
            # {'display':'block'}, 
            {'display':'none'}]




@app.callback(
    Output(component_id='stop-session', component_property='className'),
    Input(component_id="stop-session", component_property="n_clicks"),
    prevent_initial_call = True
)
def stop_session(n_clicks):
    '''Only on clicking i.e n_clicks>=1 export button would work not from starting when the app runs'''
    global session_num
    if n_clicks == 1:
        # modify session_file for the day
        modify_session_file_for_the_day(session_num)
        print('\nSESSION ENDED SUCCESSFULLY!!\n')
        os.kill(os.getpid(), signal.SIGTERM)
    return ""









@app.callback(
    Output(component_id={'type':'CardImg', 'index':MATCH}, component_property='style'),
    [Input(component_id={'type':'CardDiv', 'index':MATCH}, component_property='n_clicks'),
    Input(component_id={'type':'CardDiv', 'index':MATCH}, component_property='id'),
    ],
    prevent_initial_call = True
)
def on_hover(n_clicks, id):
    '''Only on clicking i.e n_clicks>=1 export button would work not from starting when the app runs'''

    
    print('\nInside on_hover\n')
    # print('value, id', id)
    # cardimg_index = id['index']
    # print('')
    # # if n_clicks == 1:
    # #     print('\nInside Hover Img\n')
    # return {'height':'50%',  'width':"auto"}
    print(id)
    print(n_clicks)

    if id['type'] == 'CardDiv':
        if n_clicks % 2 == 1:
            # print(n_clicks)
            # print(f"\n{id}, {id['type']}\n")

            # print('\nEnd on_hover\n')

            return   {'height':'50%',  'width':"50%", 'z-index':'20', 'position':'fixed', "top": "10%" , "left": "10%", 'margin': '-70px 0 0 -170px' }
        else:
            # print(n_clicks)
            # print(f"\n{id}, {id['type']}\n")
            # print('\nEnd on_hover\n')

            return {"height": "125px", "width": "160px", 'z-index':'3'}
    

# ================ magnify callback ===================================



#  {'height':'50%',  'width':"50%", 'z-index':'20', 'position':'fixed', "top": "10%" , "left": "10%", 'margin': '-70px 0 0 -170px' }









@app.callback(
    # Output({'type': 'label-option', 'index': MATCH}, 'labelStyle'),
    Output({'type': 'label-option', 'index': MATCH}, 'className'),
    Input({'type': 'label-option', 'index': MATCH}, 'value'),
    Input({'type': 'label-option', 'index': MATCH}, 'id'),
    prevent_initial_call = True
)
def button_click(value, id):
    '''What are the states of the radio buttons clicked?'''
    # I have the value of the recording here ,
    # Manipulate here and store in a datastructure and fire when save is clicked
    # print(f"val: {value}, id: {id}")
    print('\nStart on_click')

    global class_of_all_images
    global glob_idx
    global current_18
    global state_18
    global initial_state_18
    class_of_all_images[int(id['index'])] = int(value)
    print("class of {} set to {}".format(id['index'], value))


    for i in range(len(current_18)):
        if int(current_18[i]) == int(id['index']):
            # found the id['index' ] of the radio-button
            # for this image 
            break
    state_18[i] = int(value)
    print('\nEnd on_click\n')

    # return {'display': 'inline-block', 'color':'black', "padding": "0px 1px 0px 1px", "margin": "1px", 'fontsize':'1px'}
    return "touched"


if __name__ == '__main__':
    port = random.randrange(2000, 7999)
    # during development
    app.run_server(host='127.0.0.1', port=port, debug=True)


    # for testing
    # app.run_server(host='127.0.0.1', port=port, debug=False)


# ,  dev_tools_ui=False