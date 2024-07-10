import sys
# just for a example to not copy pysipack module here
sys.path.insert(0, '..')

from pysipack import *

pack = Pack(
    name="Cool pack",
    tag="Different",
    author="Alex",
    rounds=[]
)

space = [
    Question(100, "What is the shape of Earth?", "Sphere"),
    Question(200, Image("mars.jpg"), "Mars"),
    Question(300, "Is Pluto a planet", "No"),
]
space = Theme("Space", space)

songs = [
    Question(100, ["Name the artist", Audio("rapgod.mp3")], "Eminem"),
    Question(200, "Name the most viewed song on Youtube", "Baby Shark Dance", Audio("babyshark.mp3")),
    Question(300, ["Name the album", Image("nevermind.jpg")], "Nirvanna - Nevermind"),
]
songs = Theme("Songs", songs)

round = Round("First round", [space, songs])

flag = Question(0, Image("canada_flag_blured.jpg"), "Canada", Image("canada_flag.png"))
flag = Theme("Flag", [flag])

country = Question(0, "Most populated country", "China")
country = Theme("Country", [country])

final = Round("Final round", [flag, country], True)

pack.rounds = [round, final]
pack.save()