import telebot
import constants
import requests
import json
import time
from currency_converter import CurrencyConverter
from emoji import emojize

BOLD = '\033[1m'
END = '\033[0m'

bot = telebot.TeleBot(constants.token)

def translate_text(text):
    req_url = constants.translate_url + 'key=' + constants.translate_key + '&text=' + text + "&lang=en"
    r = requests.post(req_url)
    return r.json()['text'][0]

def write_json(data, filename='answer.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=True)
        f.close()

def log(message, answer):
    print("\n ----------------")
    from datetime import datetime
    print(datetime.now())
    print("Message from {0} {1}. ( id = {2}) \n Text: {3}".format(message.from_user.first_name, message.from_user.last_name,
                                                                  str(message.from_user.id), message.text))
    print("Answer: " + answer)

def goo_shorten_url(url):
    post_url = constants.shortener_url
    payload = {'longUrl': url}
    headers = {'content-type': 'application/json'}
    r = requests.post(post_url, data=json.dumps(payload), headers=headers)
    return r.json()['id']

#def sort_by_time(s, f):

@bot.message_handler(commands=['help'])
def handle_text(message):
    bot.send_message(message.from_user.id, """Я бот для поиска авиабилетов
Но я еще не готов к работе!""")

@bot.message_handler(commands=['start'])
def handle_text(message):
    m1="Hello, my dear friend!\n I can find the cheapest airline tickets for you! "
    m2="You have to just write some information about destinations and date in the given order:\n"
    m3="City from you will fly out "
    m4="City where you will fly "
    m5="Date of the fly or first day of the interval "
    m6="Last day of the interval(optional) "
    m7="For example:\n _Moscow - Astana - 19/05/2018_ "
    m8=" _Almaty - Kazan - 16/04/2018 - 25/04/2018_ "
    m9="*You can use any language that you want:3*"
    em1=emojize(":airplane:", use_aliases=True)
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup.row('/start', '/end')
    user_markup.row('/next', '/choose time')
    m1 = "Hello, my dear friend!\n I can find the cheapest airline tickets for you!"
    m2 = "You have to just write some information about destinations and date in the given order:\n"
    m3 = "City from you will fly out"
    m4 = "City where you will fly"
    m5 = "Date of the fly or first day of the interval"
    m6 = "Last day of the interval(optional)"
    m7 = "For example:\n Moscow - Astana - 19/05/2018"
    m8 = " Almaty - Kazan - 16/04/2018 - 25/04/2018"
    em1 = emojize(":airplane:", use_aliases=True)
    em2 = emojize(":date:", use_aliases=True)
    em3 = emojize(":small_orange_diamond:", use_aliases=True)
    em4 = emojize(":small_blue_diamond:", use_aliases=True)
    em8 = emojize(":arrow_upper_right:", use_aliases=True)
    em9 = emojize(":arrow_lower_right:", use_aliases=True)
    em5 = emojize(":white_check_mark:", use_aliases=True)

    em6 = emojize(":warning:", use_aliases=True)
    sendtext=m1+em1+"\n"+m2+em3+m3+em8+"\n"+em4+m4+em9+"\n"+em3+m5+em2+"\n"+em4+m6+em2+"\n"+m7+em5+"\n"+m8+em5+"\n\n"+em6+m9
    bot.send_message(message.from_user.id, sendtext, parse_mode="Markdown")

    sendtext = m1 + em1 + "\n" + m2 + em3 + m3 + em8 + "\n" + em4 + m4 + em9 + "\n" + em3 + m5 + em2 + "\n" + em4 + m6 + em2 + "\n" + m7 + em5 + "\n" + m8 + em5
    bot.send_message(message.from_user.id, sendtext, reply_markup=user_markup)

@bot.message_handler(commands=['end'])
def handle_text(message):
    hide_markup = telebot.types.ReplyKeyboardRemove()
    bot.send_message(message.from_user.id, "GoodBye", reply_markup=hide_markup)



@bot.message_handler(content_types=['text'])
def handle_text(message):
    bot.send_chat_action(message.from_user.id,'typing')
    answer = "Input Error! Please Try again!"
    if message.text == "Hello" or message.text == "Привет" or message.text == "Пока" or message.text == "Bye":
        answer = message.text
    elif len(message.text) > 10:
        checker = True

        if len(message.text.split("-")) == 4:
            cityFrom, cityTo, dateFrom, dateTo = message.text.split("-")
            checker = False
        elif len(message.text.split("-"))== 3:
            cityFrom, cityTo, dateFrom = message.text.split("-")
            dateTo = dateFrom
            checker = False


        if(checker == False):
            cityFrom = " ".join(cityFrom.split())
            cityTo = " ".join(cityTo.split())
            dateFrom = " ".join(dateFrom.split())
            dateTo = " ".join(dateTo.split())
            cityFrom = translate_text(cityFrom)
            cityTo = translate_text(cityTo)
            #print(cityFrom + "\n" + cityTo + "\n" + dateFrom + "\n" + dateTo)
            url = 'https://api.skypicker.com/flights?flyFrom=' + cityFrom + '&to=' + cityTo + '&dateFrom=' + dateFrom +\
                  '&dateTo=' + dateTo + '&partner=picky'
            req = requests.get(url)
            write_json(req.json())
            req_dict = req.json()
            emm1= emojize(":credit_card:", use_aliases=True)
            emm2 = emojize(":customs:", use_aliases=True)
            emm3 = emojize(":arrow_upper_right:", use_aliases=True)
            emm4 = emojize(":arrow_lower_right:", use_aliases=True)
            emm5 = emojize(":information_source:", use_aliases=True)
            emm6 = emojize(":large_blue_circle:", use_aliases=True)

            tem1 = ""
            tem2 = ""
            tem3 = ""
            if 'data' in req_dict:
                if len(req_dict['data']) == 0:
                    answer = "No tickets"
                else:
                    ticket_url = None
                    min_cost = 10000
                    for each in req_dict['data']:
                        if min_cost > each['conversion']['EUR']:
                            ticket_url = each['deep_link']
                            min_cost = each['conversion']['EUR']
                            price = each['price']
                            c = CurrencyConverter()
                            tem1 = emm2 +"*From airport:* " +  each['cityFrom'] +"\n" +emm2+"*To airport:* " + each['cityTo'] + "\n"
                            tem2 = emm3 +"*Time leaving:* " + time.strftime("%D %H:%M", time.localtime(int(each['dTime']))) + "\n" +emm4+"*Time arriving:* " + time.strftime("%D %H:%M", time.localtime(int(each['aTime'])))
                            tem3 =emm1+ "*The best Price:* €" + str(price) + " (" + str(c.convert(price,'EUR','USD'))[:6] + " USD)"+"\n"

                    answer = tem3 + tem1 + tem2 + "\n"+emm5+"*For more info:*" + goo_shorten_url(ticket_url) + "\n"
            else:
                answer = "Input Error! Please try again!"

    else:
        answer = "I don't know"
    bot.send_message(message.from_user.id, answer,parse_mode="Markdown")
    log(message, answer)


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
