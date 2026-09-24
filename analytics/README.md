# Analytics Pipeline (Module 2) - Documentation

## Part A: Missing Value Strategies & Justifications
- **Embarked / Embark_Town (0.22% Missing):** Because missingness is below 5%, these rows were simply dropped to prevent modeling on artificial geospatial data.
- **Age (19.8% Missing):** Falling into the 5%-30% threshold, this column was imputed using the median to avoid pulling the distribution via outliers.
- **Deck (77.2% Missing):** Because missingness exceeds 30%, imputation is mathematically unsound. I chose to encode missing values as 'Missing' rather than dropping the column entirely. Missing a deck assignment often correlates with lower ticket classes, meaning the *absence* of data is itself predictive.

## Part A: Outliers & Skewness
- **Fare Skewness Conclusion:** The calculations reveal that Mean (32.20) > Median (14.45) > Mode (8.05). Because the mean is pulled heavily to the right of the median and mode, the `fare` distribution is **strongly right-skewed**.

## Part A: Correlation Matrix Interpretation
The two strongest absolute off-diagonal correlations (excluding redundant columns) are:
1. **Pclass vs. Fare (-0.55):** A strong negative correlation. As passenger class numerically increases (1st to 3rd class, meaning a downgrade in quality), the fare paid decreases significantly.
2. **Pclass vs. Age (-0.37):** A moderate negative correlation. Older passengers were more likely to be in 1st class, while younger passengers and families were predominantly in 3rd class.

## Part A: Multivariate Data Story Interpretations
1. **Survival Rate by Pclass and Sex (Barplot):** Women across all classes survived at significantly higher rates than men, but a 1st class man still had a better chance of survival than a 3rd class man, indicating socio-economic status was secondary only to gender.
2. **Age vs Fare by Survival (Scatter):** Survival clusters heavily among passengers who paid high fares regardless of age. There is a distinct horizontal density at the bottom (low fare) where non-survivors are heavily concentrated.
3. **Age Distribution by Survival (Violin Plot):** The distributions show a noticeable bulge in survival for young children (age < 10), indicating prioritizing youth during evacuation. 
4. **Family Size vs Survival (Point Plot):** Passengers traveling alone or with small families (1-3 people) had the highest survival rates. Survival plummeted for large families (>4), likely because coordinating large groups during an emergency hindered escape.

## Part B: Train/Test Split Stratification
Stratification is required because the target variable `survived` is imbalanced (~38% survived). A standard random split risks creating a training set with too few survival cases, causing the model to underpredict the minority class. 

## Part B: Imbalance Strategy Conclusion
Comparing Baseline, Balanced Weights, and SMOTE on Logistic Regression:
- **Balanced Weights** yielded the highest Recall, correctly identifying more actual survivors but suffering a massive drop in Precision (more false positives).
- **SMOTE** balanced the trade-off, maintaining a solid F1 score while improving minority recall without sacrificing as much precision as the weighted method. Therefore, **SMOTE** is the best strategy when predicting survival, as it handles the decision boundary synthetically rather than just mathematically shifting weights.

## Part B: Regression Side-Task 
The residual plot displays a clear cone/fan shape, where the spread of residuals increases massively as the predicted fare increases. This is a textbook example of **heteroscedasticity**. The model struggles to accurately predict high fares (outliers), likely because our linear features cannot capture the exponential pricing jumps of 1st class luxury tickets.

## Final Recommendation
I recommend deploying the **Random Forest Classifier** to production. While Logistic Regression provided a solid baseline AUC (0.85), the tuned Random Forest achieved the highest overall Accuracy and F1 Score by effectively capturing the non-linear interactions between Age, Sex, and Pclass. Because interpretability (which favors Decision Trees) is less critical here than raw predictive power on complex interactions, the Random Forest ensemble is the most robust choice.