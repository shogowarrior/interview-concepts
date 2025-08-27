SQL Question 2: Analyzing Monthly Average Ratings of Airbnb Property Listings
Given the reviews table with columns: review_id, user_id, submit_date, listing_id, stars, write a SQL query to get the average rating of each Airbnb property listing per month. The submit_date column represents when the review was submitted. The listing_id column represents the unique ID of the Airbnb property, and stars represents the rating given by the user where 1 is the lowest and 5 is the highest rating.

reviews Example Input:
| review_id | user_id | submit_date           | listing_id | stars |
|-----------|---------|-----------------------|------------|-------|
| 6171      | 123     | 01/02/2022 00:00:00   | 50001      | 4     |
| 7802      | 265     | 01/15/2022 00:00:00   | 69852      | 4     |
| 5293      | 362     | 01/22/2022 00:00:00   | 50001      | 3     |
| 6352      | 192     | 02/05/2022 00:00:00   | 69852      | 3     |
| 4517      | 981     | 02/10/2022 00:00:00   | 69852      | 2     |
Answer:
SELECT 
EXTRACT(MONTH from submit_date) as mth, 
listing_id, 
AVG(stars) as avg_stars
FROM 
reviews
GROUP BY 
mth, 
listing_id
ORDER BY 
listing_id, 
mth;
This SQL query will first group the data by month and listing_id. For each group, it calculates the average stars rating. The EXTRACT(MONTH from submit_date) function is used to get the month from submit_date. The AVG(stars) function is used to calculate the average stars rating. In the end, it orders the results by listing_id and mth.

Example Output:
mth	listing_id	avg_stars
1	50001	3.50
1	69852	4.00
2	69852	2.50
