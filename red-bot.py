from src.modules import *

# GETTING ENVIRONMENT VARIABLES FROM .ENV FILE
BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, '.env'))
bot_token = os.getenv("BOT_TOKEN")
reddit_client_id = os.getenv("REDDIT_CLIENT_ID")
reddit_client_token = os.getenv("REDDIT_CLIENT_TOKEN")
reddit_username = os.getenv("REDDIT_USERNAME")
reddit_password = os.getenv("REDDIT_PASSWORD")
reddit_useragent = os.getenv("REDDIT_USERAGENT")
streamable_email = os.getenv("STREAMABLE_EMAIL")
streamable_password = os.getenv("STREAMABLE_PASSWORD")
imgbb_key = os.getenv("IMGBB_KEY")
client = commands.Bot(command_prefix="*", intents=discord.Intents.all())
client.remove_command('help')


# FUNCTIONS
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def get_gdir(ctx):
  gdir = os.path.join(os.getcwd(), 'reddit', str(ctx.message.guild.id))
  if not os.path.exists(gdir): os.makedirs(gdir)
  return gdir

def get_paths(ctx, path):
  gdir = get_gdir(ctx)
  subfile =  os.path.join(gdir, 'subscriptions')
  if path == 'subfile': return os.path.join(gdir, 'subscriptions')
  elif path == 'redsdvid': return os.path.join(gdir, 'reddit.mp4')
  elif path == 'redvidhd': return os.path.join(gdir, 'reddithd.mp4')
  else: return os.path.join(gdir, path + '.json')

async def reddit_auth(reddit_client_id, reddit_client_token, reddit_username, reddit_password, reddit_useragent):
    async with httpx.AsyncClient() as client:
        timeout=httpx.Timeout(60, connect=5.0, read=None, write=5.0)
        auth = httpx.BasicAuth(reddit_client_id, reddit_client_token)
        data = {'grant_type': 'password',
                'username': reddit_username,
                'password': reddit_password}
        headers = {'User-Agent': reddit_useragent}
        res = await client.post('https://www.reddit.com/api/v1/access_token',
                            auth=auth, data=data, headers=headers, timeout=timeout)
        TOKEN = res.json()['access_token']
        headers = {**headers, **{'Authorization': f"bearer {TOKEN}"}}
        return headers

# ON READY
@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))

# CLEAN UP
@client.event
async def on_message(message):
    await client.process_commands(message)
    if message.content.startswith("*") == True:
        await message.delete()

# CREATE TEXT CHANNEL
@client.command()
async def redinit(ctx):
    guild = ctx.message.guild
    cat = discord.utils.get(ctx.guild.categories, name="Text Channels")
    channel = discord.utils.get(ctx.guild.channels, name="reddit-feed")
    if channel is None:
        channel = await guild.create_text_channel('reddit-feed', category=cat)

#HELP COMMAND
# @client.command()
# async def help(ctx)




# SUBSCRIBE TO SUBREDDIT
@client.command()
async def redsub(ctx, subred):
    subreddit = subred.lower()
    subfile = get_paths(ctx, 'subfile')
    permalink = f"https://oauth.reddit.com/r/{subreddit}/.json"
    lst = []
    if os.path.exists(subfile):
        append_write = 'a'
    else:
        append_write = 'w'
    with open(subfile, 'r') as f:
        lines = f.readlines()
    for line in lines:
        lst.append(line.strip())
    if subreddit in lst:
        embed = discord.Embed(title="Already Subscribed!", description=f"r/{subreddit}", color=0xff8800)
        embed.set_thumbnail(url="https://bit.ly/3vChLsT")
        await ctx.send(embed=embed)
    else:
        headers = await reddit_auth(reddit_client_id, reddit_client_token, reddit_username, reddit_password, reddit_useragent)
        async with httpx.AsyncClient() as client:
            r = await client.get(permalink, headers=headers)
        if 'data' in r.json() and len(r.json()['data']['children']) != 0:
            with open(subfile, append_write) as f:
                f.write(subreddit + "\n")
            embed = discord.Embed(title="Subscribed successfully", description=f"r/{subreddit}", color=0xff8800)
            embed.set_thumbnail(url="https://bit.ly/3vChLsT")
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="Subreddit Not Found!", description=f"Please Check Spelling\nr/{subreddit}", color=0xff8800)
            embed.set_thumbnail(url="https://bit.ly/3vChLsT")
            await ctx.send(embed=embed)

# UNSUBSCRIBE FROM SUBREDDIT
@client.command()
async def redunsub(ctx, subreddit):
    subfile = get_paths(ctx, 'subfile')
    if os.path.exists(subfile):
        with open(subfile, 'r') as f:
            lines = f.readlines()
        with open(subfile, 'w') as f:
            for line in lines:
                if line.strip("\n") != subreddit:
                    f.write(line)
        embed = discord.Embed(title="Unsubscribed successfully", description=f"r/{subreddit}", color=0xff8800)
        embed.set_thumbnail(url="https://bit.ly/3vChLsT")
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="Subscription Not Found!", description="Please subscribe using redsub command", color=0xff8800)
        embed.set_thumbnail(url="https://bit.ly/3vChLsT")
        await ctx.send(embed=embed)

# # SHOW SUBSCRIPTIONS
# @client.command()
# async def showsub(ctx):
#     subfile = get_paths(ctx, 'subfile')
#     subs = []
#     if os.path.exists(subfile):
#         with open(subfile, 'r', encoding="utf-8") as f:
#             lines = f.readlines()
#         for line in lines:
#             subs.append(line.strip())
#             sublst = sorted(subs)
#         a = [(chunks(sublst, 5))]
#         b = (list(a[0]))
#         c = len(b)
#         count = 0
#         embeds = []
#         while count < c:
#             def get_pages():
#                 pages = []
#                 j = 0
#                 i = 0
#                 for i in range(0, c):
#                     f = eval(f"{b}[{str(i)}]")
#                     embed = discord.Embed(title="Subscription List", color=0xff8800)
#                     for x in f:
#                         embed.add_field(name='\u200b', value=f"{j+1}. r/{x}", inline=False)
#                         j += 1
#                     embed.set_thumbnail(url="https://bit.ly/3vChLsT")
#                     pages.append(embed)
#                     i += 1
#                 return pages
#             count = count + 1
#         paginator = Paginator(pages=get_pages(), compact=True, timeout=86400.0)
#         await paginator.start(ctx)

# SHOW SUBSCRIPTIONS
@client.command()
async def showsub(ctx):
    subfile = get_paths(ctx, 'subfile')
    if os.path.exists(subfile):
        with open(subfile, 'r', encoding="utf-8") as f:
            lines = f.read().splitlines()
        lines.sort()
        a = chunks(lines, 5)
        embeds = []
        j = 1
        for b in a:
            embed = discord.Embed(title="Subscription List", color=0xff8800)
            for i in b:
                embed.add_field(name='\u200b', value=f"{j}. r/{i}", inline=False)
                j += 1
            embed.set_thumbnail(url="https://bit.ly/3vChLsT")
            embeds.append(embed)
        paginator = Paginator(pages=embeds, compact=True, timeout=86400.0)
        await paginator.start(ctx)

# MANUAL SCRAPE
@client.command()
async def reddit(ctx, subredd, cat, limit):
    channel = discord.utils.get(ctx.guild.channels, name="reddit-feed")
    if channel is None:
        membed = discord.Embed(title="**#reddit-feed** Channel Not Found", description= "Please run redinit to create channel", color=0xff8800)
        membed.set_thumbnail(url="https://bit.ly/3vChLsT")
        await ctx.send(embed=membed)
    else:

        # VARIABLES AND PATHS
        pics = [".jpg", ".gif", ".png", ".jpeg"]
        subfile = get_paths(ctx, 'subfile')
        cwd = os.getcwd()
        plt = platform.system()

        # WEBDRIVER CONFIG
        geckobin = "geckodriver.exe" if plt == "Windows" else "geckodriverlinux"
        PATH = os.path.join(cwd, "src", geckobin)
        service = services.Geckodriver(binary=PATH)
        browser = browsers.Firefox()
        browser.capabilities = {
            "moz:firefoxOptions": {"args": ["--headless", "--disable-gpu"]}
        }

        # REDDIT AUTHENTICATION
        headers = await reddit_auth(reddit_client_id, reddit_client_token, reddit_username, reddit_password, reddit_useragent)
        timeout=httpx.Timeout(60, connect=5.0, read=None, write=5.0)
        async with httpx.AsyncClient() as client:
            r = await client.get(f'https://oauth.reddit.com/r/{subredd}/{cat}/.json?limit={limit}', headers=headers, timeout=timeout)
            posts = r.json()['data']['children']
            for post in posts:
                try:

                    # NEW POST EMBED
                    permalink = f"https://www.reddit.com{post['data']['permalink']}"
                    p_embed=discord.Embed(title=f"**{post['data']['title']}**", url=permalink, description=f"by {post['data']['author']}", color=0xff8800)
                    p_embed.set_author(name="New Post", url=permalink)
                    p_embed.set_footer(text=post['data']['subreddit_name_prefixed'])
                    p_embed.set_thumbnail(url="https://bit.ly/3vChLsT")
                    await channel.send(embed=p_embed)

                    # TEXT POST
                    if post['data']['selftext']:
                        vid_url = None
                        message = post['data']['selftext']

                        #SPLIT AND CONVERT TO IMAGE
                        lst = textwrap.wrap(message, width=50)
                        a = [(chunks(lst, 20))]
                        b = (list(a[0]))
                        c = len(b)
                        count = 0
                        embeds = []
                        while count < c:
                            d = (b[count])
                            spath = os.path.join(get_gdir(ctx), 'echo' + str(count) + '.png')
                            s = Spreadsheet(path=spath)
                            font = os.path.join(cwd, 'src', 'HelveticaMono.ttf')
                            for line in d:
                                cells = line.split('|')
                                s.addrow(cells, font, 18, (200,200,200))
                            fn = s.makeimg(color = (255, 255, 255, 25))

                            #UPLOAD TO IMGBB
                            client = imgbbpy.AsyncClient(imgbb_key)
                            image = await client.upload(file=spath)
                            tempVar = "imgbb"+str(count)
                            globals()[tempVar] = image.url
                            var1 = eval(tempVar)

                            # CREATE PAGINATED EMBED
                            def get_pages():
                                pages = []
                                for i in range(0, c):
                                    f = eval("imgbb" + str(i))
                                    embed = discord.Embed(title=f"**{post['data']['title']}**", url=permalink, color=0xff8800)
                                    embed.set_image(url=f)
                                    pages.append(embed)
                                return pages
                            count = count + 1
                        paginator = Paginator(pages=get_pages(), compact=True, timeout=86400.0)

                        #CLEANUP
                        dd1 = os.listdir(get_gdir(ctx))
                        for x in dd1:
                            if x.endswith(".png"):
                                os.remove(os.path.join(get_gdir(ctx), x))
                        embed = None

                    # VIDEO POST
                    elif post['data']['url'].startswith('https://v.redd.it/'):
                        paginator = None
                        v_embed = discord.Embed(title='Video Post', description='Processing Video Post, Please Be Patient!', color=0xff8800)
                        v_embed.set_thumbnail(url="https://bit.ly/3vChLsT")
                        await channel.send(embed=v_embed, delete_after=10)

                        #GET VIDEO LINKS FROM REDDITSAVE
                        async with get_session(service, browser) as session: # WEBDRIVER
                            await session.get('https://redditsave.com/')
                            x = await session.get_element('input[type="text"]')
                            await x.send_keys(permalink)
                            y = await session.get_element('button[id="download"]')
                            await y.click()
                            hd_vidurl = await session.get_url()
                            z = await session.get_element('button[class="downloadbutton"]')
                            await z.click()
                            rdsv_url = await session.get_url()
                        redsave = rdsv_url
                        hdredsave = hd_vidurl

                        # DOWNLOAD SD VIDEO
                        r = await client.get(redsave, headers = {'User-agent': reddit_useragent}, timeout=timeout)
                        src = r.content
                        soup = BeautifulSoup(src, 'lxml')
                        links = soup.find_all("a")
                        for link in links:
                            if "Download" in link.text:
                                if "240" in link.attrs['href']:
                                    redvid = link.attrs['href']
                        r = await client.get(redvid, timeout=timeout)
                        with open(get_paths(ctx, 'redsdvid'), 'wb') as f:
                            f.write(r.content)
                        fs = os.path.getsize(get_paths(ctx, 'redsdvid'))

                        # IF SD VIDEO BIGGER THAN 7.9MB UPLOAD TO STREAMABLE
                        file_size = fs / 1024000
                        if file_size > 7.9:
                            async with get_session(service, browser) as session:# WEBDRIVER
                                await session.get('https://streamable.com/login')
                                a = await session.get_element('input[type="text"]')
                                await a.click()
                                b = await session.get_element('input[type="text"]')
                                await b.send_keys(streamable_email)
                                c = await session.get_element('input[type="password"]')
                                await c.send_keys(streamable_password)
                                d = await session.get_element('button[type="submit"]')
                                await d.click()
                                await sleep(2)
                                await session.wait_for_element(5, 'span[class="text"]')
                                e = await session.get_element('input[type="file"]')
                                await sleep(2)
                                await e.send_keys(get_paths(ctx, 'redsdvid'))
                                await sleep(30)
                                f = await session.wait_for_element(5, 'a[id="video-url-input"][value]')
                                strm_url = await f.get_text()
                            vid_url = strm_url
                            await sleep(2)
                        else:

                            # DOWNLOAD HD VIDEO, CHECK SIZE AND USE IF UNDER 8MB
                            vid_url = None
                            r = await client.get(hdredsave, headers = {'User-agent': reddit_useragent}, timeout=timeout)
                            src = r.content
                            soup = BeautifulSoup(src, 'lxml')
                            links = soup.find_all("a")
                            for link in links:
                                try:
                                    if link.attrs['href'].startswith('https://ds.redditsave'):
                                        hdvid = link.attrs['href']
                                except KeyError:
                                    pass
                            r = await client.get(hdvid, timeout=timeout)

                            with open(get_paths(ctx, 'redvidhd'), 'wb') as f:
                                f.write(r.content)
                            fshd = os.path.getsize(get_paths(ctx, 'redvidhd'))
                            file_sizehd = fshd / 1024000
                            if file_sizehd < 7.9:
                                await channel.send(file=discord.File(get_paths(ctx, 'redvidhd')))
                            else:
                                await channel.send(file=discord.File(get_paths(ctx, 'redsdvid')))
                        embed = False

                    # IMAGE POST ENDS WITH PROPER EXTENSION
                    elif post['data']['url'].endswith(tuple(pics)):
                        paginator = None
                        vid_url = None
                        embed = discord.Embed(title=post['data']['title'], url=permalink, color=0xff8800)
                        embed.set_image(url=post['data']['url'])
                        embed.set_footer(text=post['data']['subreddit_name_prefixed'])
                    else:
                        paginator = None
                        vid_url = None
                        if post['data']['url_overridden_by_dest']:

                            # CHECK FOR SUPPORTED MEDIA EMBEDS AND POST LINKS DIRECTLY
                            links = ['https://gfycat.com/', 'https://youtube.com/', 'https://www.youtube.com/', 'https://youtu.be/', 'http://i.imgur.com/', 'https://imgur.com/', 'https://i.imgur.com/', 'https://streamable.com']
                            if post['data']['url_overridden_by_dest'].startswith(tuple(links)):
                                await channel.send(post['data']['url_overridden_by_dest'])
                                embed = False
                            elif 'bandcamp.com' in post['data']['url_overridden_by_dest']:
                                await channel.send(post['data']['url_overridden_by_dest'])
                                embed = False

                            # HANDLING REDDIT GALLERY IMAGES, WORK IN PROGRESS
                            elif post['data']['url_overridden_by_dest'].startswith('https://www.reddit.com/gallery/'):
                                embed = discord.Embed(title=post['data']['title'], description=post['data']['url_overridden_by_dest'], url=permalink, color=0xff8800)
                                embed.set_footer(text=post['data']['subreddit_name_prefixed'])

                            # LINK POST SEND WITHOUT EMBEDDING, WILL AUTO EMBED MOST OF THE TIME
                            else:
                                await channel.send(post['data']['url_overridden_by_dest'])
                                embed = False

                        #UNKNOWN POST USE THUMBNAIL
                        else:
                            embed = discord.Embed(title=post['data']['title'], url=permalink, color=0xff8800)
                            embed.set_image(url=post['data']['thumbnail'])
                            embed.set_footer(text=post['data']['subreddit_name_prefixed'])

                    # CHECK CONDITIONS AND SEND EMBED, MEDIA OR EMBEDDED MEDIA
                    if vid_url:
                        await channel.send(vid_url)
                    elif embed:
                        await channel.send(embed=embed)
                    elif paginator:
                        await paginator.start(ctx)
                    await sleep(3)

                # SOMETHING WENT WRONG WITH PROCESSING POST MOVE ON TO NEXT ITERATION
                except Exception:
                    pass


# SCRAPE 50 NEW POSTS PER SUBREDDIT IN SUBSCRIPTIONS
@client.command()
async def redhook(ctx):
    channel = discord.utils.get(ctx.guild.channels, name="reddit-feed")
    if channel is None:
        membed = discord.Embed(title="**#reddit-feed** Channel Not Found", description= "Please run _redinit to create channel", color=0xff8800)
        membed.set_thumbnail(url="https://bit.ly/3vChLsT")
        await ctx.send(embed=membed)
    else:

        # VARIABLES AND PATHS
        pics = [".jpg", ".gif", ".png", ".jpeg"]
        subfile = get_paths(ctx, 'subfile')
        if not os.path.exists(subfile):
            zembed = discord.Embed(title="No Subscriptions Found!", description="use _redsub command to subscribe to subreddits", color=0xff8800)
            await ctx.send(embed=zembed)

        # SUBSCRIPTIONS DATABASE
        else:
            subreddits = []
            with open(subfile, 'r') as f:
                lst = f.readlines()
                for element in lst:
                    subreddits.append(element.strip())
            plt = platform.system()
            cwd = os.getcwd()
            # WEBDRIVER CONFIG
            geckobin = "geckodriver.exe" if plt == "Windows" else "geckodriverlinux"
            PATH = os.path.join(cwd, "src", geckobin)
            service = services.Geckodriver(binary=PATH)
            browser = browsers.Firefox()
            browser.capabilities = {
                "moz:firefoxOptions": {"args": ["--headless", "--disable-gpu"]}
            }

            # REDDIT AUTHENTICATION
            headers = await reddit_auth(reddit_client_id, reddit_client_token, reddit_username, reddit_password, reddit_useragent)
            timeout=httpx.Timeout(60, connect=5.0, read=None, write=5.0)
            # CHECK FOR DB FILE, IF NOT EXISTS CREATE
            for sub in subreddits:
                try:
                    js_file = get_paths(ctx, sub)
                    with open(js_file) as json_file:
                        db = json.load(json_file)
                except FileNotFoundError:
                    db = []

                #POPULATE DB
                async with httpx.AsyncClient() as client:
                    await sleep(0)
                    r = await client.get(f'https://oauth.reddit.com/r/{sub}/top/.json?t=day', headers=headers, timeout=timeout)
                try:
                    posts = r.json()['data']['children']
                    pass
                except KeyError:
                    continue

                #PROCESS 50 NEW POSTS
                for post in posts:
                    try:
                        if post['data']['name'] not in db:
                            db.append(post['data']['name'])
                            with open(js_file, 'w') as outfile:
                                json.dump(db[-50:], outfile, indent=2)
                            permalink = f"https://www.reddit.com{post['data']['permalink']}"
                            p_embed=discord.Embed(title=f"**{post['data']['title']}**", url=permalink, description=f"by {post['data']['author']}", color=0xff8800)
                            p_embed.set_author(name="New Post", url=permalink)
                            p_embed.set_footer(text=post['data']['subreddit_name_prefixed'])
                            p_embed.set_thumbnail(url="https://bit.ly/3vChLsT")
                            await channel.send(embed=p_embed)

                            # TEXT POST
                            if post['data']['selftext']:
                                vid_url = None

                                #SPLIT AND CONVERT TO IMAGE
                                message = post['data']['selftext']
                                lst = textwrap.wrap(message, width=50)
                                a = [(chunks(lst, 20))]
                                b = (list(a[0]))
                                c = len(b)
                                count = 0
                                embeds = []
                                while count < c:
                                    d = (b[count])
                                    spath = os.path.join(get_gdir(ctx), 'echo' + str(count) + '.png')
                                    s = Spreadsheet(path=spath)
                                    font = os.path.join(cwd, 'src', 'HelveticaMono.ttf')
                                    for line in d:
                                        cells = line.split('|')
                                        s.addrow(cells, font, 18, (200,200,200))
                                    fn = s.makeimg(color = (255, 255, 255, 25))

                                    #UPLOAD TO IMGBB
                                    client = imgbbpy.AsyncClient(imgbb_key)
                                    image = await client.upload(file=spath)
                                    tempVar = "imgbb"+str(count)
                                    globals()[tempVar] = image.url
                                    var1 = eval(tempVar)

                                    # CREATE PAGINATED EMBED
                                    def get_pages():
                                        pages = []
                                        for i in range(0, c):
                                            f = eval("imgbb" + str(i))
                                            embed = discord.Embed(title=f"**{post['data']['title']}**", url=permalink, color=0xff8800)
                                            embed.set_image(url=f)
                                            pages.append(embed)
                                        return pages
                                    count = count + 1
                                paginator = Paginator(pages=get_pages(), compact=True, timeout=86400.0)
                                dd1 = os.listdir(get_gdir(ctx))

                                #CLEANUP
                                for x in dd1:
                                    if x.endswith(".png"):
                                        os.remove(os.path.join(get_gdir(ctx), x))
                                embed = None

                            # VIDEO POST
                            elif post['data']['url'].startswith('https://v.redd.it/'):
                                paginator = None
                                v_embed = discord.Embed(title='Video Post', description='Processing Video Post, Please Be Patient!', color=0xff8800)
                                v_embed.set_thumbnail(url="https://bit.ly/3vChLsT")
                                await channel.send(embed=v_embed, delete_after=5)

                                #GET VIDEO LINKS FROM REDDITSAVE
                                async with get_session(service, browser) as session:
                                    await session.get('https://redditsave.com/')
                                    x = await session.get_element('input[type="text"]')
                                    await x.send_keys(permalink)
                                    y = await session.get_element('button[id="download"]')
                                    await y.click()
                                    hd_vidurl = await session.get_url()
                                    z = await session.get_element('button[class="downloadbutton"]')
                                    await z.click()
                                    rdsv_url = await session.get_url()
                                redsave = rdsv_url
                                hdredsave = hd_vidurl

                                # DOWNLOAD SD VIDEO
                                async with httpx.AsyncClient() as client:
                                    await sleep(0)
                                    r = await client.get(redsave, headers = {'User-agent': reddit_useragent}, timeout=timeout)
                                    src = r.content
                                    soup = BeautifulSoup(src, 'lxml')
                                    links = soup.find_all("a")
                                    for link in links:
                                        if "Download" in link.text:
                                            if "240" in link.attrs['href']:
                                                redvid = link.attrs['href']
                                    r = await client.get(redvid, timeout=timeout)
                                with open(get_paths(ctx, 'redsdvid'), 'wb') as f:
                                    f.write(r.content)
                                fs = os.path.getsize(get_paths(ctx, 'redsdvid'))

                                # IF SD VIDEO BIGGER THAN 7.9MB UPLOAD TO STREAMABLE
                                file_size = fs / 1024000
                                if file_size > 7.9:
                                    async with get_session(service, browser) as session:
                                        await session.get('https://streamable.com/login')
                                        a = await session.get_element('input[type="text"]')
                                        await a.click()
                                        b = await session.get_element('input[type="text"]')
                                        await b.send_keys(streamable_email)
                                        c = await session.get_element('input[type="password"]')
                                        await c.send_keys(streamable_password)
                                        d = await session.get_element('button[type="submit"]')
                                        await d.click()
                                        await sleep(2)
                                        await session.wait_for_element(5, 'span[class="text"]')
                                        e = await session.get_element('input[type="file"]')
                                        await sleep(2)
                                        await e.send_keys(get_paths(ctx, 'redsdvid'))
                                        await sleep(30)
                                        f = await session.wait_for_element(5, 'a[id="video-url-input"][value]')
                                        strm_url = await f.get_text()
                                    vid_url = strm_url
                                    await sleep(2)
                                else:

                                    # DOWNLOAD HD VIDEO, CHECK SIZE AND USE IF UNDER 8MB
                                    vid_url = None
                                    async with httpx.AsyncClient() as client:
                                        await sleep(0)
                                        r = await client.get(hdredsave, headers = {'User-agent': reddit_useragent}, timeout=timeout)
                                        src = r.content
                                        soup = BeautifulSoup(src, 'lxml')
                                        links = soup.find_all("a")
                                        for link in links:
                                            try:
                                                if link.attrs['href'].startswith('https://ds.redditsave'):
                                                    hdvid = link.attrs['href']
                                            except KeyError:
                                                pass
                                        r = await client.get(hdvid, timeout=timeout)

                                    with open(get_paths(ctx, 'redvidhd'), 'wb') as f:
                                        f.write(r.content)
                                    fshd = os.path.getsize(get_paths(ctx, 'redvidhd'))
                                    file_sizehd = fshd / 1024000
                                    if file_sizehd < 7.9:
                                        await channel.send(file=discord.File(get_paths(ctx, 'redvidhd')))
                                    else:
                                        await channel.send(file=discord.File(get_paths(ctx, 'redsdvid')))
                                embed = False

                            # IMAGE POST ENDS WITH PROPER EXTENSION
                            elif post['data']['url'].endswith(tuple(pics)):
                                paginator = None
                                vid_url = None
                                embed = discord.Embed(title=post['data']['title'], url=permalink, color=0xff8800)
                                embed.set_image(url=post['data']['url'])
                                embed.set_footer(text=post['data']['subreddit_name_prefixed'])
                            else:
                                paginator = None
                                vid_url = None
                                if post['data']['url_overridden_by_dest']:

                                    # CHECK FOR SUPPORTED MEDIA EMBEDS AND POST LINKS DIRECTLY
                                    links = ['https://gfycat.com/', 'https://youtube.com/', 'https://www.youtube.com/', 'https://youtu.be/', 'http://i.imgur.com/', 'https://imgur.com/', 'https://i.imgur.com/', 'https://streamable.com']
                                    if post['data']['url_overridden_by_dest'].startswith(tuple(links)):
                                        await channel.send(post['data']['url_overridden_by_dest'])
                                        embed = False
                                    elif 'bandcamp.com' in post['data']['url_overridden_by_dest']:
                                        await channel.send(post['data']['url_overridden_by_dest'])
                                        embed = False

                                    # HANDLING REDDIT GALLERY IMAGES, WORK IN PROGRESS
                                    elif post['data']['url_overridden_by_dest'].startswith('https://www.reddit.com/gallery/'):
                                        embed = discord.Embed(title=post['data']['title'], description=post['data']['url_overridden_by_dest'], url=permalink, color=0xff8800)
                                        embed.set_footer(text=post['data']['subreddit_name_prefixed'])

                                    # LINK POST SEND WITHOUT EMBEDDING, WILL AUTO EMBED MOST OF THE TIME
                                    else:
                                        await channel.send(post['data']['url_overridden_by_dest'])
                                        embed = False

                                #UNKNOWN POST USE THUMBNAIL
                                else:
                                    embed = discord.Embed(title=post['data']['title'], url=permalink, color=0xff8800)
                                    embed.set_image(url=post['data']['thumbnail'])
                                    embed.set_footer(text=post['data']['subreddit_name_prefixed'])

                            # CHECK CONDITIONS AND SEND EMBED, MEDIA OR EMBEDDED MEDIA
                            if vid_url:
                                await channel.send(vid_url)
                            elif embed:
                                await channel.send(embed=embed)
                            elif paginator:
                                await paginator.start(ctx)
                            await sleep(3)

                    # SOMETHING WENT WRONG WITH PROCESSING POST MOVE ON TO NEXT ITERATION
                    except Exception:
                        pass


            # ending the loop if user doesn't react after x seconds



# REDHOOK TASK LOOP
# @tasks.loop(seconds=86400)
# async def redtask(reddit_client_id, reddit_client_token, reddit_username, reddit_password, reddit_useragent):
#
#     # VARIABLES AND PATHS
#     await client.wait_until_ready()
#     cwd = os.getcwd()
#     guilds = os.listdir(os.path.join(cwd, 'reddit'))
#     for gld in guilds:
#         guild = client.get_guild(int(gld))
#         gdir = os.path.join(cwd, 'reddit', gld)
#         channel = get(guild.channels, name="reddit-feed")
#         pics = [".jpg", ".gif", ".png", ".jpeg"]
#         subfile = os.path.join(cwd, 'reddit', gld, 'subscriptions')
#
#         #SUBSCRIPTION DB
#         subreddits = []
#         with open(subfile, 'r') as f:
#             lst = f.readlines()
#             for element in lst:
#                 subreddits.append(element.strip())
#         plt = platform.system()
#         cwd = os.getcwd()
#
#         # WEBDRIVER CONFIG
#         geckobin = "geckodriver.exe" if plt == "Windows" else "geckodriverlinux"
#         PATH = os.path.join(cwd, "src", geckobin)
#         service = services.Geckodriver(binary=PATH)
#         browser = browsers.Firefox()
#         browser.capabilities = {
#             "moz:firefoxOptions": {"args": ["--headless", "--disable-gpu"]}
#         }
#         headers = await reddit_auth(reddit_client_id, reddit_client_token, reddit_username, reddit_password, reddit_useragent)
#         timeout=httpx.Timeout(60, connect=5.0, read=None, write=5.0)
#         for sub in subreddits:
#             try:
#                 js_file = os.path.join(gdir, sub + '.json')
#                 with open(js_file) as json_file:
#                     db = json.load(json_file)
#             except FileNotFoundError:
#                 db = []
#
#             async with httpx.AsyncClient() as req:
#                 await sleep(0)
#                 r = await req.get(f'https://oauth.reddit.com/r/{sub}/top/.json?t=day', headers=headers, timeout=timeout)
#             try:
#                 posts = r.json()['data']['children']
#                 pass
#             except KeyError:
#                 continue
#
#             for post in posts:
#                 # try:
#                 if post['data']['name'] not in db:
#                     db.append(post['data']['name'])
#                     with open(js_file, 'w') as outfile:
#                         json.dump(db[-50:], outfile, indent=2)
#                     permalink = f"https://www.reddit.com{post['data']['permalink']}"
#                     p_embed=discord.Embed(title=f"**{post['data']['title']}**", url=permalink, description=f"by {post['data']['author']}", color=0xff8800)
#                     p_embed.set_author(name="New Post", url=permalink)
#                     p_embed.set_footer(text=post['data']['subreddit_name_prefixed'])
#                     p_embed.set_thumbnail(url="https://bit.ly/3vChLsT")
#                     await channel.send(embed=p_embed)
#
#                     # TEXT POST
#                     if post['data']['selftext']:
#                         vid_url = None
#
#                         #SPLIT AND CONVERT TO IMAGE
#                         message = post['data']['selftext']
#                         lst = textwrap.wrap(message, width=50)
#                         a = [(chunks(lst, 20))]
#                         b = (list(a[0]))
#                         c = len(b)
#                         count = 0
#                         embeds = []
#                         while count < c:
#                             d = (b[count])
#                             spath = os.path.join(gdir, 'echo' + str(count) + '.png')
#                             s = Spreadsheet(path=spath)
#                             font = os.path.join(cwd, 'src', 'HelveticaMono.ttf')
#                             for line in d:
#                                 cells = line.split('|')
#                                 s.addrow(cells, font, 18, (200,200,200))
#                             fn = s.makeimg(color = (255, 255, 255, 25))
#
#                             #UPLOAD TO IMGBB
#                             imgbbclient = imgbbpy.AsyncClient(imgbb_key)
#                             image = await imgbbclient.upload(file=spath)
#                             tempVar = "imgbb"+str(count)
#                             globals()[tempVar] = image.url
#                             var1 = eval(tempVar)
#                             async def paginate():
#                                 embeds = [
#                                     Embed(title="test page 1", description="This is just some test content!", color=0x115599),
#                                     Embed(title="test page 2", description="Nothing interesting here.", color=0x5599ff),
#                                     Embed(title="test page 3", description="Why are you still here?", color=0x191638)
#                                 ]
#
#                                 paginator = BotEmbedPaginator(embeds)
#                                 await paginator.run()

# redtask.start(reddit_client_id, reddit_client_token, reddit_username, reddit_password, reddit_useragent)


client.run(bot_token)
