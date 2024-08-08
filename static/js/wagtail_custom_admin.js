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
}
