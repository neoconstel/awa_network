// this section of the script should only be executed if on the
// url path: /admin/account/ (for now it's not perfect but works good).
// It hides the default email field, as it causes terribe issues

if (window.location.href.includes("/account")) {
  // Do something if the current URL contains "/admin/account"
  const default_email_field = document.querySelector("#id_name_email-email");
  default_email_field.value = "thisEmailField@isNotSubmitted.com";
  default_email_field.parentElement.parentElement.parentElement.hidden = true;
  console.log("Hidden faulty email field from admin setting");
}
