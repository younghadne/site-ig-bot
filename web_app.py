from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading
import time
import random
import json
import os
from datetime import datetime
from instagrapi import Client

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'instagram-bot-secret')
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

bot_state = {
    'running': False,
    'cl': None,
    'username': None,
    'stats': {
        'followers_gained': 0, 'likes_given': 0, 'unfollowed': 0,
        'stories_viewed': 0, 'dms_sent': 0, 'accounts_processed': 0,
        'start_time': None,
    },
}

def load_saved_session():
    """Try to load a saved session if available"""
    try:
        import glob
        session_files = glob.glob("sessions/*.json")
        log(f"🔍 Checking for saved sessions... Found {len(session_files)} files")
        if session_files:
            latest_file = max(session_files, key=os.path.getmtime)
            log(f"📂 Found saved session: {latest_file}")
            
            cl = Client()
            cl.delay_range = [3, 6]
            log(f"📖 Loading session file...")
            cl.load_settings(latest_file)
            
            # Verify session still works
            try:
                log(f"🔐 Verifying session is still valid...")
                user_info = cl.account_info()
                username = user_info.username
                bot_state['cl'] = cl
                bot_state['username'] = username
                log(f"✅ Loaded saved session as @{username}")
                return True
            except Exception as e:
                log(f"⚠️ Saved session verification failed: {str(e)[:100]}")
                log("⚠️ Saved session expired, need to login again")
                return False
        else:
            log("ℹ️ No saved sessions found, need to login")
    except Exception as e:
        log(f"⚠️ Could not load session: {str(e)[:100]}")
        import traceback
        log(f"🔧 Traceback: {traceback.format_exc()[:200]}")
    return False

def log(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    socketio.emit('log', {'message': f"[{timestamp}] {message}"})

def update_stats():
    socketio.emit('stats', bot_state['stats'])

def human_delay(base=2.0, jitter=0.3):
    time.sleep(base * random.uniform(1 - jitter, 1 + jitter))

# ==================== INSTAGRAM ACTIONS ====================

def do_search_and_follow(target, max_followers, follow_limit):
    cl = bot_state['cl']
    if not cl:
        log("❌ Not logged in!"); return
    try:
        log(f"🔍 Starting follow process for target: @{target}")
        log(f"📊 Max followers to fetch: {max_followers}, Daily limit: {follow_limit}")
        
        log(f"🔍 Looking up user ID for @{target}...")
        user_id = cl.user_id_from_username(target)
        log(f"✅ Found user ID: {user_id}")
        
        log(f"👥 Fetching followers list (max {max_followers})...")
        followers = cl.user_followers(user_id, amount=max_followers)
        log(f"👥 Successfully fetched {len(followers)} followers")
        
        followed = 0
        skipped = 0
        for uid, user_info in followers.items():
            if not bot_state['running']:
                log("⏸️ Bot stopped by user")
                break
            if bot_state['stats']['followers_gained'] >= follow_limit:
                log(f"🎯 Daily follow limit reached ({follow_limit})")
                break
            
            try:
                uname = user_info.username if hasattr(user_info, 'username') else str(uid)
                log(f"👤 Attempting to follow @{uname}...")
                cl.user_follow(uid)
                bot_state['stats']['followers_gained'] += 1
                followed += 1
                log(f"✅ Followed @{uname} ({followed}/{max_followers}) | Total: {bot_state['stats']['followers_gained']}/{follow_limit}")
                update_stats()
                human_delay(base=3.0)
                
                if followed % 15 == 0:
                    log("😴 Taking a break (anti-detection)...")
                    time.sleep(random.uniform(30, 60))
                    
            except Exception as e:
                skipped += 1
                log(f"⚠️ Could not follow @{uname}: {str(e)[:60]}")
                human_delay(base=2.0)
        
        bot_state['stats']['accounts_processed'] += 1
        update_stats()
        log(f"✅ Done with @{target}: {followed} followed, {skipped} skipped")
        
    except Exception as e:
        log(f"❌ Error in do_search_and_follow: {str(e)}")
        import traceback
        log(f"🔧 Traceback: {traceback.format_exc()[:300]}")

def do_auto_unfollow(max_unfollows):
    cl = bot_state['cl']
    if not cl:
        log("❌ Not logged in!"); return
    try:
        log(f"🔄 Auto-unfollow (max: {max_unfollows})...")
        following = cl.user_following(cl.user_id)
        log(f"📊 You follow {len(following)} users")
        unfollowed = 0
        for uid, user_info in following.items():
            if not bot_state['running'] or unfollowed >= max_unfollows:
                break
            try:
                uname = user_info.username if hasattr(user_info, 'username') else str(uid)
                cl.user_unfollow(uid)
                unfollowed += 1
                bot_state['stats']['unfollowed'] += 1
                log(f"✅ Unfollowed @{uname} ({unfollowed}/{max_unfollows})")
                update_stats()
                human_delay(base=3.0)
                if unfollowed % 10 == 0:
                    log("😴 Break from unfollowing...")
                    time.sleep(random.uniform(30, 60))
            except Exception as e:
                log(f"⚠️ Skip: {str(e)[:50]}")
        log(f"✅ Unfollowed {unfollowed} users")
    except Exception as e:
        log(f"❌ Error: {str(e)}")

def do_auto_like_feed(num_likes):
    cl = bot_state['cl']
    if not cl:
        log("❌ Not logged in!"); return
    try:
        log(f"❤️ Auto-like feed (max: {num_likes})...")
        feed = cl.get_timeline_feed()
        liked = 0
        for item in feed:
            if not bot_state['running'] or liked >= num_likes:
                break
            try:
                pk = item.pk if hasattr(item, 'pk') else item.id
                cl.media_like(pk)
                liked += 1
                bot_state['stats']['likes_given'] += 1
                log(f"❤️ Liked post #{liked}/{num_likes}")
                update_stats()
                human_delay(base=2.0)
                if liked % 15 == 0:
                    log("😴 Break from liking...")
                    time.sleep(random.uniform(20, 40))
            except Exception as e:
                log(f"⚠️ Skip: {str(e)[:50]}")
        log(f"✅ Liked {liked} posts")
    except Exception as e:
        log(f"❌ Error: {str(e)}")

def do_mass_story_view(max_stories):
    cl = bot_state['cl']
    if not cl:
        log("❌ Not logged in!"); return
    try:
        log(f"👁️ Mass story view (max: {max_stories})...")
        feed = cl.get_timeline_feed()
        viewed = 0
        for item in feed:
            if not bot_state['running'] or viewed >= max_stories:
                break
            try:
                user_pk = item.user.pk if hasattr(item, 'user') and hasattr(item.user, 'pk') else None
                if not user_pk:
                    continue
                stories = cl.user_stories(user_pk)
                for story in stories:
                    if not bot_state['running'] or viewed >= max_stories:
                        break
                    story_pk = story.pk if hasattr(story, 'pk') else story.id
                    cl.story_seen([story_pk])
                    viewed += 1
                    bot_state['stats']['stories_viewed'] += 1
                    log(f"👁️ Viewed story #{viewed}/{max_stories}")
                    update_stats()
                    human_delay(base=1.5)
            except:
                continue
        log(f"✅ Viewed {viewed} stories")
    except Exception as e:
        log(f"❌ Error: {str(e)}")

def do_auto_dm(target, message):
    cl = bot_state['cl']
    if not cl:
        log("❌ Not logged in!"); return
    try:
        log(f"💬 Sending DM to @{target}...")
        user_id = cl.user_id_from_username(target)
        cl.direct_send(message, [user_id])
        bot_state['stats']['dms_sent'] += 1
        log(f"✅ DM sent to @{target}")
        update_stats()
    except Exception as e:
        log(f"❌ DM error: {str(e)}")

def do_approve_requests():
    cl = bot_state['cl']
    if not cl:
        log("❌ Not logged in!"); return
    try:
        log("✅ Approving follow requests...")
        pending = cl.user_pending_follow_requests()
        approved = 0
        for req in pending:
            try:
                uid = req.pk if hasattr(req, 'pk') else req.id
                cl.approve_pending_follow_request(uid)
                approved += 1
                uname = req.username if hasattr(req, 'username') else str(uid)
                log(f"✅ Approved @{uname}")
                human_delay(base=1.0)
            except Exception as e:
                log(f"⚠️ Skip: {str(e)[:50]}")
        log(f"✅ Approved {approved} requests")
    except Exception as e:
        log(f"❌ Error: {str(e)}")

def do_like_user_posts(target, num_likes):
    cl = bot_state['cl']
    if not cl:
        log("❌ Not logged in!"); return
    try:
        log(f"❤️ Liking {num_likes} posts from @{target}...")
        user_id = cl.user_id_from_username(target)
        medias = cl.user_medias(user_id, amount=num_likes)
        liked = 0
        for media in medias:
            if not bot_state['running'] or liked >= num_likes:
                break
            try:
                pk = media.pk if hasattr(media, 'pk') else media.id
                cl.media_like(pk)
                liked += 1
                bot_state['stats']['likes_given'] += 1
                log(f"❤️ Liked #{liked}/{num_likes} from @{target}")
                update_stats()
                human_delay(base=2.0)
            except Exception as e:
                log(f"⚠️ Skip: {str(e)[:50]}")
        log(f"✅ Liked {liked} posts from @{target}")
    except Exception as e:
        log(f"❌ Error: {str(e)}")

# ==================== MAIN BOT LOOP ====================

def run_bot_loop(targets, follow_limit, like_limit, followers_per_account):
    try:
        log("🚀 Starting bot loop...")
        
        # Check if logged in
        if not bot_state['cl']:
            log("❌ No active session found. Please login first.")
            bot_state['running'] = False
            socketio.emit('bot_status', {'running': False})
            return
        else:
            log(f"✅ Using existing session as @{bot_state['username']}")
        
        target_accounts = [t.strip() for t in targets.split(',') if t.strip()]
        if not target_accounts:
            log("❌ No target accounts specified!")
            bot_state['running'] = False
            socketio.emit('bot_status', {'running': False})
            return
        
        log(f"🎯 Target accounts: {', '.join(['@' + a for a in target_accounts])}")
        log(f"📊 Daily follow limit: {follow_limit}")
        log(f"📊 Followers per account: {followers_per_account}")
        log(f"📊 Current followers gained: {bot_state['stats']['followers_gained']}")
        
        loop_count = 0
        while bot_state['running'] and bot_state['stats']['followers_gained'] < follow_limit:
            loop_count += 1
            log(f"🔄 === Loop #{loop_count} ===")
            random.shuffle(target_accounts)
            
            for target in target_accounts:
                if not bot_state['running']:
                    log("⏸️ Bot stopped by user")
                    break
                if bot_state['stats']['followers_gained'] >= follow_limit:
                    log(f"🎯 Daily follow limit reached ({follow_limit})")
                    break
                
                log(f"🎯 Processing target: @{target}")
                do_search_and_follow(target, followers_per_account, follow_limit)
                log(f"⏸️ Delay before next target...")
                human_delay(base=5.0)
        
        log("🎉 Bot session completed!")
        log(f"📊 Final stats: {bot_state['stats']['followers_gained']} followers gained")
        
    except Exception as e:
        log(f"❌ Bot error: {str(e)}")
        import traceback
        log(f"🔧 Traceback: {traceback.format_exc()[:300]}")
    finally:
        bot_state['running'] = False
        socketio.emit('bot_status', {'running': False})

# ==================== FLASK ROUTES ====================

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def on_connect():
    emit('bot_status', {'running': bot_state['running']})
    emit('stats', bot_state['stats'])
    
    # Try to load saved session automatically
    if not bot_state['cl']:
        if load_saved_session():
            emit('login_status', {'success': True, 'username': bot_state.get('username', '')})

@socketio.on('password_login')
def on_password_login(data):
    username = data.get('username', '')
    password = data.get('password', '')
    log(f"📡 Password login requested for @{username}...")
    def login_thread():
        try:
            cl = Client()
            cl.delay_range = [3, 6]
            cl.login(username, password)
            bot_state['cl'] = cl
            bot_state['username'] = username
            
            # Save session for reuse
            os.makedirs("sessions", exist_ok=True)
            cl.dump_settings(f"sessions/{username}.json")
            log(f"💾 Session saved for @{username}")
            
            log(f"✅ Logged in as @{username}")
            emit('login_status', {'success': True, 'username': username})
        except Exception as e:
            log(f"❌ Password login failed: {str(e)[:100]}")
            emit('login_status', {'success': False})
    threading.Thread(target=login_thread, daemon=True).start()

@socketio.on('login')
def on_login(data):
    # Redirect to password login
    on_password_login(data)

@socketio.on('start_bot')
def on_start(data):
    if bot_state['running']:
        log("⚠️ Bot already running"); return
    bot_state['running'] = True
    bot_state['stats'] = {
        'followers_gained': 0, 'likes_given': 0, 'unfollowed': 0,
        'stories_viewed': 0, 'dms_sent': 0, 'accounts_processed': 0,
        'start_time': time.time(),
    }
    t = threading.Thread(target=run_bot_loop, args=(
        data.get('targets', ''), int(data.get('follow_limit', 120)),
        int(data.get('like_limit', 50)), int(data.get('followers_per_account', 10)),
    ), daemon=True)
    bot_state['thread'] = t
    t.start()
    emit('bot_status', {'running': True})

@socketio.on('stop_bot')
def on_stop():
    bot_state['running'] = False
    emit('bot_status', {'running': False})
    log("🛑 Bot stopped by user")

@socketio.on('auto_unfollow')
def on_unfollow(data):
    if not bot_state['cl']:
        log("❌ Login first!"); return
    threading.Thread(target=do_auto_unfollow, args=(int(data.get('limit', 50)),), daemon=True).start()

@socketio.on('auto_like_feed')
def on_like_feed(data):
    if not bot_state['cl']:
        log("❌ Login first!"); return
    threading.Thread(target=do_auto_like_feed, args=(int(data.get('limit', 20)),), daemon=True).start()

@socketio.on('mass_story_view')
def on_mass_story(data):
    if not bot_state['cl']:
        log("❌ Login first!"); return
    threading.Thread(target=do_mass_story_view, args=(int(data.get('limit', 50)),), daemon=True).start()

@socketio.on('auto_dm')
def on_dm(data):
    if not bot_state['cl']:
        log("❌ Login first!"); return
    msg = data.get('message', '') or "Hey! Thanks for following me 🙏"
    threading.Thread(target=do_auto_dm, args=(data.get('target', ''), msg), daemon=True).start()

@socketio.on('approve_requests')
def on_approve():
    if not bot_state['cl']:
        log("❌ Login first!"); return
    threading.Thread(target=do_approve_requests, daemon=True).start()

@socketio.on('like_user_posts')
def on_like_user(data):
    if not bot_state['cl']:
        log("❌ Login first!"); return
    threading.Thread(target=do_like_user_posts, args=(data.get('target', ''), int(data.get('limit', 3))), daemon=True).start()

@socketio.on('reset_stats')
def on_reset():
    bot_state['stats'] = {
        'followers_gained': 0, 'likes_given': 0, 'unfollowed': 0,
        'stories_viewed': 0, 'dms_sent': 0, 'accounts_processed': 0,
        'start_time': None,
    }
    emit('stats', bot_state['stats'])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    socketio.run(app, debug=debug, host='0.0.0.0', port=port)
