from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.groups.models import SolidarityGroup, GroupMember
from apps.notifications.models import Notification
from apps.common.models import AuditLog
from apps.common.signals import log_action


@receiver(post_save, sender=SolidarityGroup)
def log_group_creation(sender, instance, created, **kwargs):
    if created:
        log_action(
            AuditLog.Action.CREATE, 'SolidarityGroup', instance.id,
            f"Groupe {instance.nom} ({instance.get_type_display()})",
            f"Region: {instance.region}, Agent: {instance.agent}"
        )
        # Notify the group agent
        if instance.agent:
            Notification.objects.create(
                titre=f"Groupe {instance.nom} cree",
                message=f"Le groupe solidaire {instance.nom} ({instance.get_type_display()}) a ete cree dans la region {instance.region}.",
                type=Notification.Type.SYSTEME,
                user=instance.agent.user,
            )


@receiver(post_save, sender=GroupMember)
def notify_group_member_added(sender, instance, created, **kwargs):
    if created:
        role_labels = dict(GroupMember.RoleChoices.choices)
        log_action(
            AuditLog.Action.CREATE, 'GroupMember', instance.id,
            f"Membre: {instance.client} -> {instance.groupe.nom}",
            f"Client: {instance.client.user.get_full_name()}, Groupe: {instance.groupe.nom}, Role: {role_labels.get(instance.role, instance.role)}"
        )
        # Notify the new member
        Notification.objects.create(
            titre=f"Adhesion au groupe {instance.groupe.nom}",
            message=f"Vous avez ete ajoute au groupe solidaire {instance.groupe.nom} en tant que {role_labels.get(instance.role, instance.role)}.",
            type=Notification.Type.SYSTEME,
            user=instance.client.user,
        )
        # Notify the group agent
        if instance.groupe.agent:
            Notification.objects.create(
                titre=f"Nouveau membre: {instance.client.user.get_full_name()}",
                message=f"{instance.client.user.get_full_name()} a rejoint le groupe {instance.groupe.nom} en tant que {role_labels.get(instance.role, instance.role)}.",
                type=Notification.Type.SYSTEME,
                user=instance.groupe.agent.user,
            )


@receiver(post_delete, sender=GroupMember)
def notify_group_member_removed(sender, instance, **kwargs):
    log_action(
        AuditLog.Action.DELETE, 'GroupMember', instance.id,
        f"Membre retire: {instance.client} -> {instance.groupe.nom}",
        f"Client: {instance.client.user.get_full_name()}, Groupe: {instance.groupe.nom}"
    )
    # Notify the removed member
    Notification.objects.create(
        titre=f"Retrait du groupe {instance.groupe.nom}",
        message=f"Vous avez ete retire du groupe solidaire {instance.groupe.nom}.",
        type=Notification.Type.SYSTEME,
        user=instance.client.user,
    )