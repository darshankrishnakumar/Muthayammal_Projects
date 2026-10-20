# 02 — Mathematical Modeling & Physical Kinematics

## Physical Principles
Vehicle collision dynamics are governed by conservation of momentum, Newton's second law, and structural plastic deformation mechanics:

$$\vec{F}_{impact} = m \cdot \vec{a}(t) = \frac{d\vec{p}}{dt}$$

$$\Delta v = \int_{t_0}^{t_0 + \Delta t} a(t) \, dt$$

## The 5 Physical Kinematic Cues
1. **Trajectory Deviation ($d_{traj}$)**:
   $$d_{traj} = \|\vec{p}_{centroid}(t) - \vec{p}_{lane\_centerline}(t)\|$$
   Excursion exceeding 2.5 meters beyond lane boundaries triggers geometric anomaly alerts.

2. **Longitudinal Deceleration Peak ($a_{decel}$)**:
   Normal braking achieves $a_{decel} \le 0.8g$. Emergency ABS braking reaches $1.0g - 1.4g$. Structural crash impacts generate instantaneous peaks:
   $$a_{peak} \ge 3.0g \quad (\approx 29.4 \text{ m/s}^2)$$

3. **Abnormal Orientation & Rollover Yaw ($\theta_{yaw}$)**:
   Vehicle orientation is tracked via bounding box principal axis angles:
   $$\omega_{yaw} = \frac{d\theta_{yaw}}{dt} > 120^\circ/\text{s}$$
   Aspect ratio inversion $AR = \frac{w}{h} < 0.8$ accompanied by rapid yaw indicates catastrophic vehicle rollover.

4. **Collision Proximity & Convergence**:
   Inter-vehicle distance vector $\Delta \vec{r}_{ij} = \vec{p}_i - \vec{p}_j$ and closing speed $\dot{r}_{ij} < 0$. Bounding box intersection over union (IoU) exceeding threshold confirms physical contact.

5. **Post-Impact Immobility ($\tau_{immobile}$)**:
   $$\tau_{immobile} = t_{current} - t_{arrest} \quad \text{where } v(t) < 1.0 \text{ km/h}$$
   Safe hard braking resumes motion within 1.0 to 3.0 seconds ($\tau_{immobile} = 0$). True structural crashes produce persistent immobilization ($\tau_{immobile} > 15\text{s}$).

## Dynamic Attention Gating Equation
The learned attention gate weighs physical cues against visual temporal features:
$$\vec{\alpha} = \sigma\left(W_{gate} \cdot \vec{k} + b_{gate}\right) \in [0, 1]^5$$
$$\vec{F}_{fused} = \text{LayerNorm}\left(\vec{k}_{proj} + \text{MultiHeadAttention}(\vec{k}_{proj}, \vec{v}_{temporal}, \vec{v}_{temporal})\right)$$
$$\vec{F}_{out} = [\vec{F}_{fused} \, \| \, (\vec{k} \odot \vec{\alpha})]$$
