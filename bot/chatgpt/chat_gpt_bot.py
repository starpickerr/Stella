import time
from bot.bot import Bot
from revChatGPT.revChatGPT import Chatbot
from common.log import logger

config = {
    "Authorization": "<Your Bearer Token Here>",  # This is optional
    "session_token": "REMOVED_HISTORICAL_CREDENTIAL"
}
chatbot = Chatbot(config)
user_session = dict()
last_session_refresh = time.time()


class ChatGPTBot(Bot):
    def reply(self, query, context=None):

        from_user_id = context['from_user_id']
        logger.info("[GPT]query={}, user_id={}, session={}".format(query, from_user_id, user_session))

        now = time.time()
        global last_session_refresh
        if now - last_session_refresh > 60 * 8:
            logger.info('[GPT]session refresh, now={}, last={}'.format(now, last_session_refresh))
            chatbot.refresh_session()
        last_session_refresh = now

        if from_user_id in user_session:
            if time.time() - user_session[from_user_id]['last_reply_time'] < 60 * 5:
                chatbot.conversation_id = user_session[from_user_id]['conversation_id']
                chatbot.parent_id = user_session[from_user_id]['parent_id']
            else:
                chatbot.reset_chat()
        else:
            chatbot.reset_chat()

        logger.info("[GPT]convId={}, parentId={}".format(chatbot.conversation_id, chatbot.parent_id))

        try:
            res = chatbot.get_chat_response(query, output="text")
            logger.info("[GPT]userId={}, res={}".format(from_user_id, res))

            user_cache = dict()
            user_cache['last_reply_time'] = time.time()
            user_cache['conversation_id'] = res['conversation_id']
            user_cache['parent_id'] = res['parent_id']
            user_session[from_user_id] = user_cache
            return res['message']
        except Exception as e:
            logger.error(e)
            return None
