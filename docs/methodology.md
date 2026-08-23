# Methodology & Algorithm Reference - Compass AI

## 1. Skill Gap Numerical Mapping
- `none` = 0
- `beginner` = 1
- `intermediate` = 2
- `advanced` = 3

Gap calculation:
$$\text{Gap} = \text{Required Level} - \text{Current User Level}$$

## 2. Priority Scoring Formula
$$\text{Priority Score} = \text{Goal Importance (1-10)} \times \text{Gap Score} \times \text{Prerequisite Factor}$$

Categories:
- **NOW:** High score & zero unsatisfied prerequisites.
- **NEXT:** High score & prerequisites in progress.
- **LATER:** Lower importance or deep prerequisite dependency.
- **SKIP:** Already mastered or not relevant to goal.
