# Cognitive Load and Hick's Law

Cognitive load is the amount of working-memory effort a task demands. Working
memory is severely limited (the classic estimate is about seven items, more
recent estimates are closer to four), so interfaces that force users to hold
many things in mind feel difficult regardless of how pretty they look.

Designers distinguish intrinsic load (inherent to the task), extraneous load
(caused by poor presentation), and germane load (effort spent building
understanding). Good interface design cannot remove intrinsic load but
should ruthlessly reduce extraneous load: consistent layouts, recognition
over recall, chunking information, and progressive disclosure (showing
advanced options only when needed).

Hick's Law (also Hick-Hyman Law) says decision time grows with the logarithm
of the number of choices: more options, slower decisions. This is why long
undifferentiated menus feel slow and why good designs group options into
categories. It also underlies the advice to limit navigation menus to a
handful of items.

For conversational interfaces there is an interesting trade-off: a chatbot
has no visible menu at all, which eliminates choice overload but creates a
discoverability problem -- users do not know what they can ask. Providing
example questions, as our chatbot does on its start screen, is the standard
mitigation.
