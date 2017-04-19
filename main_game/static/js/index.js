/**
 * Created by aark on 2017-04-18.
 */
$(function () {

    $('#btn-new-game').click(function (e) {
        var name = $('#input-game-name').val().trim();

         if (name === '') {
            $('#errors').text('Please write your game name.');
            return;
        }

        $.ajax({
            url: '/create_new_game',
            data: {name: name},
            success: function (result) {
                if (result === 'game-created') {
                    window.location.replace('/games/' + name);
                }
            },
            error: function (result) {
                if (result.responseText === 'game-exists') {
                    $('#errors').text('Game already exists.');
                }
                if (result.responseText === 'no-fancy-names') {
                    $('#errors').text('No fancy characters allowed in your name!');
                }

            }
        });


    });

    $('#btn-continue-game').click(function (e) {
        var name = $('#input-game-name').val().trim();

        if (name === '') {
            $('#errors').text('Please write your game name.');
            return;
        }

        $.ajax({
            url: '/validate_game',
            data: {name: name},
            success: function (result) {
                if (result === 'game-exists') {
                    window.location.replace('/games/' + name);
                }
            },
            error: function (result) {
                if (result.responseText === 'game-doesnt-exist') {
                    $('#errors').text('Game doesn\'t exist.');
                }
            }
        });

    });
});