window.onload = function () {
  // always run this, to show that script is working on current admin page
  console.log(
    `Executed wagtail custom_admin javascript on path:  ${window.location.href}`
  );

  // this section of the script should only be executed if on the
  // url path: /admin/account/ (for now it's not perfect but works good).
  // It hides the default email field, as it causes terribe issues

  if (
    window.location.href.includes("/account") ||
    window.location.href.includes("/adminaccount")
  ) {
    // Do something if the current URL contains "/adminaccount"
    const default_email_field = document.querySelector("#id_name_email-email");
    default_email_field.value = "thisEmailField@isNotSubmitted.com";
    default_email_field.parentElement.parentElement.parentElement.hidden = true;
    console.log("Hidden faulty email field from admin setting");
  } else if (window.location.href.includes("/adminusers")) {
    // Do something if the current URL contains "/adminusers"
    const username_tab = document.querySelector(
      "#listing-results > table > thead > tr > th.username > a"
    );
    if (username_tab != undefined) {
      username_tab.innerText = "Email";
      console.log("Renamed the 'Username' tab to 'Email'");
    }
  } else if (window.location.href.includes("/adminreviews")) {
    // Do something if the current URL contains "/adminreviews"
    window.addEventListener("click", () => {
      // select links with contents: Edit, Inspect, Delete respectively
      const popupLinks = document.querySelectorAll(".tippy-content div a");

      popupLinks.forEach((link) => {
        if (link.innerText == "Edit") {
          let href = link.href.split("/edit");
          const newHref = href[0].slice(0, -1).replace("admin", "") + href[1];
          link.href = newHref;
          link.innerText = "Crosscheck and Approve";
          link.target = "_blank"; // open in new tab
        } else if (link.innerText == "Inspect") {
          link.remove();
        }
      });
    });
  }

  // DO THESE IN ALL CASES IN THE WAGTAIL ADMIN
  if (window.location.href.includes("/admin")) {
    // Do something if the current URL includes "/admin"

    const pendingReviews = updatePendingReviews();
  }
};

async function updatePendingReviews() {
  // get domain, not including ending '/'
  const domain = window.location.origin;
  const url = domain + "/api/reviews/pending/";

  fetch(url)
    .then((response) => response.json())
    .then((data) => {
      const pendingReviewsElement = document.querySelector(
        "a[href='/adminreviews/'] span"
      );

      pendingReviewsElement.textContent = `Pending Reviews(${data.pending_reviews})`;
      console.log("updated Pending Reviews count display");
    })
    .catch((error) => console.log(error));
}
