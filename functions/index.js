const functions = require("firebase-functions");
const admin = require("firebase-admin");
const stripe = require("stripe")("process.env.STRIPE_SECRET_KEY");

admin.initializeApp();

exports.handleStripeWebhook = functions.https.onRequest((req, res) => {
  const sig = req.headers["stripe-signature"];
  const endpointSecret = "process.env.STRIPE_WEBHOOK_SECRET";

  let event;

  try {
    event = stripe.webhooks.constructEvent(req.rawBody, sig, endpointSecret);
  } catch (err) {
    console.error("Webhook signature verification failed.", err.message);
    return res.status(400).send(`Webhook Error: ${err.message}`);
  }

  // Handle successful payment
  if (event.type === "checkout.session.completed") {
    const session = event.data.object;
    const customerEmail = session.customer_email;

    if (customerEmail) {
      admin.firestore().collection("users").doc(customerEmail).set({
        pro: true
      }, { merge: true });
    }
  }

  res.status(200).send("Received webhook");
});
