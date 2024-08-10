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
  setTimeout(() => {
    const filterButton = document.querySelector(
      "#filters-drilldown > div > button"
    );
    filterButton.click();
    const approvedFilter = document.querySelector(
      "#tippy-3 > div > div > div > div > div.w-drilldown__menu > button"
    );
    approvedFilter.click();
    const radioLabel = document.querySelector(
      "#id_approved > div:nth-child(3) > label"
    );
    radioLabel.click();
    const radioButtonAll = document.querySelector("#id_approved_0");
    const radioButtonYes = document.querySelector("#id_approved_1");
    const unwantedButtons = [radioButtonAll, radioButtonYes];
    unwantedButtons.forEach((btn) => {
      btn.disabled = true;
    });
  }, 10);

  setTimeout(() => {
    const filterButton = document.querySelector(
      "#filters-drilldown > div > button"
    );
    const approveClearButton = document.querySelector(
      "#listing-results > ul > li > button.w-pill__remove"
    );
    filterButton.click();
    approveClearButton.disabled = true;
    console.log(
      "Set Reviews filter to display only reviews with approved=False"
    );
  }, 1000);
} else if (window.location.href.endsWith("/admin")) {
  // Do something if the current URL ends with "/admin"
  const pendingReviewsLink = document.querySelector(
    "#wagtail-sidebar > div > div > nav > ul > li:nth-child(4) > a > div > span"
  );

  /**
   * TODO:
   * - write an API view that simply returns number of unapproved reviews via JSON
   * - then in this wagtail_custom_admin.js, use it to get number of unapproved reviews
   * - set that number within the innerText of pendingReviewsLink (which is in the wagtail menu)
   */
}
