# Feature Proposal: Autonomous Room Discovery

## Summary

Enable NerdCarX to autonomously explore and map its environment, creating a semantic map with named locations (e.g., "kitchen", "living room") that enables natural navigation commands like "drive to the kitchen".

---

## Motivation

**Current state:** Robot can avoid obstacles reactively but has no spatial memory or understanding of its environment.

**Desired state:** Robot builds a mental model of its surroundings, recognizes rooms, and can navigate to named locations on command.

**Why auto-discovery over pre-mapping:**
- More impressive/engaging user experience
- Adapts when furniture moves
- Aligns with the "intelligent companion" vision
- Leverages existing LLM + YOLO capabilities

---

## Core Capabilities

### 1. Visual SLAM Mapping
- Build occupancy grid using monocular camera
- Track robot position within the map
- Detect when returning to visited areas (loop closure)

### 2. Frontier-Based Exploration
- Identify unexplored edges of the map ("frontiers")
- Autonomously navigate to frontiers
- Continue until environment is fully mapped

### 3. Semantic Room Labeling
- Use YOLO to detect room-identifying objects (fridge → kitchen, bed → bedroom)
- Use LLM vision for contextual room identification
- Store named waypoints with map coordinates

### 4. Natural Language Navigation
- New LLM tool: `navigate_to(location: string)`
- Lookup location in semantic map
- Path planning with obstacle avoidance

---

## User Interactions

```
User: "Explore the house"
Robot: Begins autonomous exploration, announces discoveries
       "I found what looks like a kitchen"
       "There's a bedroom down this hallway"
       "Exploration complete. I mapped 4 rooms."

User: "Drive to the kitchen"
Robot: Navigates to saved kitchen waypoint

User: "Where are you?"
Robot: "I'm in the living room, near the couch"

User: "What rooms do you know?"
Robot: "Kitchen, living room, bedroom, and bathroom"
```

---

## Hardware Considerations

**Minimum (existing hardware):**
- OV5647 camera - functional but limited FOV

**Recommended upgrade (~$10):**
- Wide-angle lens adapter (120°+ FOV)
- Improves SLAM feature tracking significantly

**Optional upgrade (~$25):**
- IMX219 wide-angle camera
- Better low-light performance

---

## Dependencies

- Monocular VSLAM library (ORB-SLAM3, RTAB-Map, or Stella-VSLAM)
- Path planning algorithm (A*, RRT, or Nav2)
- Ultrasonic sensor for scale calibration
- Existing YOLO + LLM infrastructure

---

## Suggested Phase

**Phase 4 or 5** - After core Pi integration (Phase 3) is complete.

This feature builds on:
- Working motor control ✓
- Camera integration ✓
- LLM function calling ✓
- YOLO object detection ✓

---

## Success Criteria

1. Robot can explore a multi-room environment autonomously
2. Correctly identifies and labels at least 3 room types
3. Successfully navigates to named rooms on voice command
4. Re-localizes after being moved/turned off
5. Updates map when environment changes

---

## Open Questions

- Store maps persistently or rebuild on startup?
- How to handle multi-floor environments?
- Should robot announce discoveries or stay quiet during exploration?
- Integration with future smart home features?

---

## Related Ideas

- **Patrol mode**: Periodic autonomous rounds for security
- **Object memory**: "Where did I last see my keys?"
- **Person following**: Track and follow a specific person
- **Return to charger**: Navigate to charging station when low battery
