from ursina import *
from ursina.shaders import lit_with_shadows_shader
import random

app = Ursina()

Sky(texture="sky_default")

blocks = []
gold_entities = []
shadow_entities = []  # List to store shadow entities
score = 0
timer_duration = 30  # Set the duration of the game timer in seconds
timer = timer_duration

player_entity = Entity(
    model='plane',
    texture='bucket.png',
    scale=(3, 3, 3),
    collider='box',
    position=(0, 2, 0),  # Set the starting position
    origin_y=0.5  # Adjust the origin to the middle of the bucket
)

score_panel = Panel(
    model='quad',
    color=color.rgba(0, 0, 0, 150),  # Black color with some transparency
    scale=(0.3, 0.1),  # Adjust the scale to fit the score text
    position=(0.01, 0.45),  # Adjust the position behind the score text
)

score_text = Text(
    text=f"Score: {score}",
    color=color.blue,
    position=(0, 0.45),
    origin=(0, 0),
    scale=2,
)

timer_text = Text(
    text=f"Time: {timer}s",
    color=color.red,
    position=(0.5, 0.45),
    origin=(0, 0),
    scale=2,
)

# Endgame screen elements
endgame_panel = Panel(
    model='quad',
    color=color.rgba(0, 0, 0, 200),
    scale=(0.5, 0.5),
    enabled=False,
)

endgame_text = Text(
    text="Game Over",
    color=color.white,
    position=(0, 0.1),
    origin=(0, 0),
    scale=4,
    enabled=False,
)


play_again_button = Button(
    text="Play Again",
    color=color.green,
    scale=(0.1, 0.05),
    position=(0, -0.3),
    origin=(0, 0),
    enabled=False,
)

# Directional light for shadows
directional_light = DirectionalLight(shadows=True, rotation=(45, -45, 45))

def spawn_gold():
    # Calculate random positions within the middle of the larger baseplate boundaries
    x_position = random.uniform(-10, 10)
    z_position = random.uniform(-10, 10)
    while not (-10 <= x_position <= 10 and -10 <= z_position <= 10):
        x_position = random.uniform(-10, 10)
        z_position = random.uniform(-10, 10)

    gold_scale = random.uniform(0.5, 1.5)
    gold = Entity(
        model='sphere',
        texture='goldNugget.png',
        scale=(gold_scale, gold_scale, gold_scale),
        position=(x_position, 20, z_position),
        collider='sphere',
        shader=lit_with_shadows_shader  # Apply shadow-enabled shader
    )

    # Create shadow entity
    shadow = Entity(
        model='sphere',
        color=color.rgb(50, 50, 50),  # Dark gray color for the shadow
        scale=(gold_scale * 1.1, gold_scale * 0.1, gold_scale * 1.1),  # Adjust as needed
        position=(x_position, .1, z_position),  # Place the shadow on the baseplate
        collider='sphere',
    )

    gold_entities.append(gold)
    shadow_entities.append(shadow)

def show_endgame_screen():
    endgame_panel.enabled = True
    endgame_text.enabled = True

    play_again_button.enabled = True

def update():
    global score, timer

    if timer > 0:
        # Player movement handling
        move_direction = Vec3(0, 0, 0)

        if held_keys['d']:
            move_direction.x += .4
        if held_keys['a']:
            move_direction.x -= .4
        if held_keys['w']:
            move_direction.z += .4
        if held_keys['s']:
            move_direction.z -= .4

        move_direction.normalize()
        player_entity.position += move_direction * 0.2

        for gold, shadow in zip(gold_entities, shadow_entities):
            gold.y -= 0.1
            shadow.y = 0  # Keep the shadow at the baseplate level

            if gold.y < 0:
                gold_entities.remove(gold)
                shadow_entities.remove(shadow)
                destroy(gold)
                destroy(shadow)

            # Check for collision between gold and bucket or baseplate
            if player_entity and gold and player_entity.position and gold.position:
                distance_to_gold = (player_entity.position - gold.position).length()
                if distance_to_gold < (
                        player_entity.scale.x + gold.scale.x) * .28 and gold.y >= -2:  # Check if gold is close enough to the center of the bucket
                    if gold.y >= 0:  # Check if the collision is with the bucket
                        score += 1
                        score_text.text = f"Score: {score}"
                    gold_entities.remove(gold)
                    shadow_entities.remove(shadow)
                    destroy(gold)
                    destroy(shadow)

        # Update timer
        timer -= time.dt
        timer_text.text = f"Time: {int(timer)}s"
    else:
        timer_text.text = "Time's up!"
        show_endgame_screen()

    if random.random() < 0.02 and timer > 0:
        spawn_gold()

def play_again():
    global score, timer
    score = 0
    timer = timer_duration

    # Reset UI elements
    score_text.text = f"Score: {score}"
    timer_text.text = f"Time: {timer}s"

    # Enable gameplay elements
    endgame_panel.enabled = False
    endgame_text.enabled = False

    play_again_button.enabled = False

def input(key):
    if key == 'escape':
        application.quit()

    if key == 'space' and endgame_panel.enabled:
        play_again()

play_again_button.on_click = play_again  # Set the button's click event

# Create the larger baseplate with buttons
for i in range(30):
    for j in range(30):
        block = Button(
            color=color.white,
            model='cube',
            position=(j - 15, 0, i - 15),
            texture='brick',
            parent=scene,
            origin_y=0.5
        )
        blocks.append(block)

# Adjust the starting camera position and rotation
camera.position = (0, 30, -60)  # Near the front of the larger baseplate
camera.rotation_x = 25

app.run()
