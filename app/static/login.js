/**
 * Created by sherry on 16/4/5.
 */
jQuery(document).ready(function($) {
    var $form_modal = $('.qiushi-login-modal'),
        $login_signup_button = $('.login_signup_button');

    //弹出窗口
    $login_signup_button.on('click', function (event) {

        if ($(event.target).is($login_signup_button)) {
            $(this).children('ul').toggleClass('is-visible');
        } else {
            $login_signup_button.children('ul').removeClass('is-visible');
            $form_modal.addClass('is-visible');
        }

    });

    //关闭弹出窗口
    $('.qiushi-login-modal').on('click', function (event) {
        if ($(event.target).is($form_modal) || $(event.target).is('.navbar'))  {
            $form_modal.removeClass('is-visible');
        }
    });
    //使用Esc键关闭弹出窗口
    $(document).keyup(function (event) {
        if (event.which == '27') {
            $form_modal.removeClass('is-visible');
        }
    });
});