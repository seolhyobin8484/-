import discord
import os
from discord import app_commands
from discord.ext import commands
import war_excel
from dotenv import load_dotenv

from war_excel import user_profile

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbxlrX5aerZJR38Bl3VAYo0bzyYH7ycRmuPOjfPnWseRFzMEqUTn4EZywU1L_fDHY3-F/exec "

# 티어별 색상을 반환하는 함수 추가
def get_tier_color(tier_text):
    tier = str(tier_text).upper().strip()

    # 1. 특정 키워드가 포함되어 있는지 먼저 확인 (우선순위 고려)
    # 'S3~B'처럼 브론즈가 섞여 있으면 브론즈가 우선되어야 함
    if "I" in tier :    return 0x5D4037
    if "B" in tier :    return 0xA0522D 

    # 2. 나머지 티어 검사
    if "C" in tier :    return 0xb9f3f7
    if "GM" in tier :   return 0xff1414
    if "M" in tier :    return 0x9B59B6
    if "D" in tier :    return 0x3498DB
    if "E" in tier :    return 0x2ECC71
    if "P" in tier :    return 0x1ABC9C
    if "G" in tier :    return 0xF1C40F
    if "S" in tier :    return 0x95A5A6
    
    return 0xFFFFFF

class aclient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.tree = app_commands.CommandTree(self)
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await self.tree.sync()
            self.synced = True
        print(f"Logged in as {self.user}")

client = aclient()

@client.tree.command(name="신청", description="태초마을 내전 프로필을 작성합니다.")
async def apply(interaction: discord.Interaction):
    await interaction.response.send_message(
        "https://forms.gle/eh2EpwgnwPsZGYFC9"
    )

@client.tree.command(name="정보", description="선택한 유저의 내전 정보를 알려줍니다.")
async def profile(interaction: discord.Interaction, user: discord.Member = None):
    # 대상을 지정하지 않으면 명령어를 친 유저 본인이 대상이 됨
    user = user or interaction.user
    discord_id = user.name 

    # 1. 엑셀에서 티어 정보 가져오기 (색상 결정을 위해 먼저 가져옴)
    tier_info = user_profile.get_toprate(discord_id)
    embed_color = get_tier_color(tier_info)

    # 3. 임베드 메시지 구성 (색상 적용)
    embed = discord.Embed(title=f"{user.display_name}님의 프로필", color=embed_color)
    
    embed.set_thumbnail(url=user.display_avatar.url)
    
    embed.add_field(name="롤 아이디", value=user_profile.get_lol_id(discord_id), inline=True)
    embed.add_field(name="최고 티어", value=tier_info, inline=True)
    embed.add_field(name=":trophy: 레이팅", value=user_profile.get_totalscore(discord_id), inline=False)
    embed.add_field(name="내전 승률", value=user_profile.get_win_rate(discord_id), inline=False)
    # embed.add_field(name="", value="", inline=False) 
    # embed.add_field(name="라인별 승률", value=user_profile.get_lane_win_rates(discord_id), inline=False)

@client.tree.command(name="세부정보", description="선택한 유저의 내전 정보를 세부적으로 알려줍니다.")
async def profile(interaction: discord.Interaction, user: discord.Member = None):

    # 💡 [가장 중요] 함수가 시작하자마자 0.1초 만에 "생각 중..." 상태로 만들어 3초 제한을 깨부숩니다.
    await interaction.response.defer()
    
    # 대상을 지정하지 않으면 명령어를 친 유저 본인이 대상이 됨
    user = user or interaction.user
    discord_id = user.name 

    # 1. 엑셀에서 티어 정보 가져오기 (색상 결정을 위해 먼저 가져옴)
    tier_info = user_profile.get_toprate(discord_id)
    embed_color = get_tier_color(tier_info)

    # 3. 임베드 메시지 구성 (색상 적용)
    embed = discord.Embed(title=f"{user.display_name}님의 프로필", color=embed_color)
    
    embed.set_thumbnail(url=user.display_avatar.url)
    
    embed.add_field(name="롤 아이디", value=user_profile.get_lol_id(discord_id), inline=True)
    embed.add_field(name="최고 티어", value=tier_info, inline=True)
    embed.add_field(name=":trophy: 레이팅", value=user_profile.get_totalscore(discord_id), inline=False)
    embed.add_field(name="내전 승률", value=user_profile.get_win_rate(discord_id), inline=False)
    embed.add_field(name="라인별 승률", value=user_profile.get_lane_win_rates(discord_id), inline=False)
    
    await interaction.followup.send(embed=embed)      
    

@client.tree.command(name="랭킹", description="태초마을 내전 승률 (Top 5위까지 집계)")
async def profile(interaction: discord.Interaction):
   
    embed = discord.Embed(title=f":trophy:태초마을 랭킹:trophy:", color=0xFEFD48)
    embed.add_field(name="", value="", inline=False) 
    embed.add_field(name="", value="", inline=False) 
    embed.add_field(name="", value="", inline=False) 
    
    embed.add_field(
    name="**승률**",
    value=war_excel.get_win_rating_top5_table(),
    inline=False
    )
    embed.add_field(name="",value="",inline=False)
    embed.add_field(name="",value="",inline=False)

    embed.add_field(
    name="**최다 승**",
    value=war_excel.get_most_wins_top5_table(),
    inline=False
    )
    embed.add_field(name="",value="",inline=False)
    embed.add_field(name="",value="",inline=False)
    embed.add_field(
    name="**경기수**",
    value=war_excel.get_most_plays_top5_table(),
    inline=False
    )
    
    await interaction.response.send_message(embed=embed)

@client.event
async def on_ready():
    
    try:
        # 💡 [핵심 해결책] 변경된 슬래시 명령어들을 디스코드 서버에 강제로 새로고침(동기화) 합니다.
        synced = await client.tree.sync()
        print(f"🔄 슬래시 명령어 {len(synced)}개 동기화 완료!")
    except Exception as e:
        print(f"❌ 동기화 중 에러 발생: {e}")




import aiohttp



class MatchControlView(discord.ui.View):
  def __init__(self):
      super().__init__(timeout=None) # 버튼이 영구적으로 작동하도록 세팅

  async def call_sheet_api(self, interaction: discord.Interaction, action: str, success_msg: str):
      """구글 시트 앱스크립트를 찔러서 함수를 실행시키는 도우미 함수"""
      await interaction.response.defer(ephemeral=True) # 봇이 생각 중... 상태 돌입
      
      async with aiohttp.ClientSession() as session:
          # URL 뒤에 ?action=swap 같은 파라미터를 붙여서 호출합니다.
          async with session.get(f"{WEB_APP_URL}?action={action}") as response:
              if response.status == 200:
                  result_text = await response.text()
                  await interaction.followup.send(f"✅ {success_msg} ({result_text})", ephemeral=True)
              else:
                  await interaction.followup.send("❌ 구글 시트 연동에 실패했습니다.", ephemeral=True)

  # 1. 블루팀 승리 버튼
  @discord.ui.button(label="🔵 블루팀 승리", style=discord.ButtonStyle.primary, custom_id="btn_blue_win")
  async def blue_win_button(self, interaction: discord.Interaction, button: discord.ui.Button):
      await self.call_sheet_api(interaction, "blueWin", "블루팀 승리를 기록했습니다.")

  # 2. 레드팀 승리 버튼
  @discord.ui.button(label="🔴 레드팀 승리", style=discord.ButtonStyle.danger, custom_id="btn_red_win")
  async def red_win_button(self, interaction: discord.Interaction, button: discord.ui.Button):
      await self.call_sheet_api(interaction, "redWin", "레드팀 승리를 기록했습니다.")

  # 3. 팀 맞바꾸기 버튼
  @discord.ui.button(label="🔄 팀 맞바꾸기", style=discord.ButtonStyle.secondary, custom_id="btn_swap_teams")
  async def swap_button(self, interaction: discord.Interaction, button: discord.ui.Button):
      await self.call_sheet_api(interaction, "swap", "진영을 맞바꿨습니다.")

@client.tree.command(name="내전제어", description="내전 대진표 및 기록을 제어합니다.")
async def match_control(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🏆 10인 내전 관리 시스템",
        description="아래 버튼을 누르면 구글 시트에 실시간으로 기록 및 동기화됩니다.",
        color=0x2ecc71
    )
    embed.add_field(name="🔵 BLUE TEAM", value="S10:S14 라인 유저", inline=True)
    embed.add_field(name="🔴 RED TEAM", value="S22:S26 라인 유저", inline=True)
    
    # 위에서 만든 버튼 뷰(View)를 결합해서 전송합니다
    await interaction.response.send_message(embed=embed, view=MatchControlView())



if __name__ == "__main__":
    if not TOKEN:
        raise ValueError(".env 파일에서 DISCORD_TOKEN을 찾을 수 없습니다.")
    client.run(TOKEN)