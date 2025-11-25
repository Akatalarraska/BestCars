/* jshint esversion: 8 */

const express = require('express');
const mongoose = require('mongoose');
const fs = require('fs');
const cors = require('cors');

const app = express();
const port = 3030;

app.use(cors());
app.use(require('body-parser').urlencoded({ extended: false }));

const reviewsData = JSON.parse(fs.readFileSync("reviews.json", 'utf8'));
const dealershipsData = JSON.parse(fs.readFileSync("dealerships.json", 'utf8'));

mongoose.connect("mongodb://mongo_db:27017/", {
  dbName: 'dealershipsDB'
});

const Reviews = require('./review');
const Dealerships = require('./dealership');

try {
  Reviews.deleteMany({}).then(() => {
    Reviews.insertMany(reviewsData.reviews);
  });

  Dealerships.deleteMany({}).then(() => {
    Dealerships.insertMany(dealershipsData.dealerships);
  });

} catch (error) {
  console.log("Startup insert error:", error);
}


// Home
app.get('/', async (req, res) => {
  res.send("Welcome to the Mongoose API");
});


// Fetch all reviews
app.get('/fetchReviews', async (req, res) => {
  try {
    const documents = await Reviews.find();
    res.json(documents);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching documents' });
  }
});


// Fetch reviews by dealer
app.get('/fetchReviews/dealer/:id', async (req, res) => {
  try {
    const documents = await Reviews.find({
      dealership: req.params.id
    });
    res.json(documents);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching documents' });
  }
});


// Fetch all dealers
app.get('/fetchDealers', async (req, res) => {
  try {
    const documents = await Dealerships.find();
    res.json(documents);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching dealerships' });
  }
});


// Fetch dealers by state
app.get('/fetchDealers/:state', async (req, res) => {
  try {
    const documents = await Dealerships.find({ state: req.params.state });
    res.json(documents);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching dealerships' });
  }
});


// Fetch dealer by ID
app.get('/fetchDealer/:id', async (req, res) => {
  try {
    const document = await Dealerships.findOne({ id: req.params.id });

    if (document) {
      res.json(document);
    } else {
      res.status(404).json({ error: "Dealership not found" });
    }

  } catch (error) {
    res.status(500).json({ error: 'Error fetching dealership by id' });
  }
});


// Insert review
app.post('/insert_review', express.raw({ type: '*/*' }), async (req, res) => {

  const data = JSON.parse(req.body);
  const documents = await Reviews.find().sort({ id: -1 });
  
  const newId = documents[0].id + 1;

  const review = new Reviews({
    id: newId,
    name: data.name,
    dealership: data.dealership,
    review: data.review,
    purchase: data.purchase,
    purchase_date: data.purchase_date,
    car_make: data.car_make,
    car_model: data.car_model,
    car_year: data.car_year
  });

  try {
    const savedReview = await review.save();
    res.json(savedReview);
  } catch (error) {
    console.log(error);
    res.status(500).json({ error: 'Error inserting review' });
  }
});


// Start server
app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
