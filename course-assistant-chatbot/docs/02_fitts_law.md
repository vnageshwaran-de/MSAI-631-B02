# Fitts's Law

Fitts's Law is one of the oldest and most reliable quantitative laws in HCI.
It predicts the time required to move a pointer to a target: movement time
increases with the distance to the target and decreases with the size of the
target. Formally, MT = a + b * log2(2D/W), where D is the distance to the
target and W is the width of the target.

The practical consequences show up everywhere in interface design. Bigger
buttons are faster to click. Targets at the edge or corner of the screen are
effectively infinite in size because the cursor stops there, which is why the
macOS menu bar and Windows Start button corner are so fast to hit. Context
menus that appear at the cursor location minimize distance and are therefore
fast.

Fitts's Law was formulated by Paul Fitts in 1954 from studies of human motor
control, well before graphical interfaces existed, and it transferred to the
mouse and touchscreens remarkably well. In touch interfaces it motivates
minimum touch-target sizes (Apple recommends at least 44x44 points). It is a
standard tool for comparing input devices and for arguing about button
placement in design reviews.
